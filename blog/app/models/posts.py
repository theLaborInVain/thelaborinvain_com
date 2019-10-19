"""
    The Post model lives here (at the bottom).

    Up top, we've got helper methods for working with posts.

"""

# standard lib
from datetime import datetime
from copy import copy

# second party imports
import flask
import flask_login
from bson.objectid import ObjectId

# application imports
from app import app, models, util
from app.models import images

#
#   Helper Methods
#

def get(count=10, return_type=None):
    """ This returns posts as browser-friendly JSON. """

    # get posts
    posts = app.config['MDB'].posts.find().limit(count).sort('created_on', -1)

    # now, loop through them and fancy them up
    output = []
    for post in posts:
        post_object = Post(_id=post['_id'])
        output.append(post_object.serialize())

    return output


class Tag(models.Model):
    """ Tags are very simple little guys. """

    def __init__(self, *args, **kwargs):

        models.Model.__init__(self,  *args, **kwargs)
        self.collection = 'tags'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {'name': str}
        self.required_attribs = ['name']

        self.load()


class Attachment(models.Model):
    """ Attachments are always associated with a post via post_id. Do not create
    one with out a post_id. Same-same for image_id: these have to have both. """

    def __init__(self, *args, **kwargs):

        models.Model.__init__(self,  *args, **kwargs)
        self.collection = 'attachments'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            'post_id': ObjectId,
            'image_id': ObjectId,
            'caption': str,
            'sort_order': int,
        }

        self.required_attribs = [
            'image_id',
            'post_id',
        ]

        self.load()


    def new(self):
        """ Defauls some attribs. """
        self.sort_order = 0
        super().new()


    def serialize(self):
        """ Expands the image_id onto a pseudo attrib called 'image'. """
        output = copy(self.record)
        output['image'] = images.expand_image(output['image_id'])
        return output


class Post(models.Model):
    """ Posts are complex objects and this is their base class. Their various
    types are objects that use this model as their base. """

    def __init__(self, *args, **kwargs):

        models.Model.__init__(self,  *args, **kwargs)
        self.collection = 'posts'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            # content
            'title': str,
            'handle': str,
            'body': str,
            'lede': str,
            'tags': list,
            'hero_image': ObjectId,
            'hero_caption': str,        # just a string

            # meta
            'created_by': ObjectId,
            'created_on': datetime,
            'updated_on': datetime,
            'published_on': datetime,
            'published': bool,
        }

        self.load()


    def new(self):
        """ Creates a new post, does a heckin' save. """

        for req_var in ['title', 'hero_image']:
            if req_var not in self.kwargs:
                err = "The '%s' kwarg is required when creating a new post!"
                raise ValueError(err % req_var)

        # create the record
        self._id = self.mdb.insert({'title': self.title})

        # finally, attribs and save
        self.created_on = datetime.now()
        self.created_by = flask_login.current_user._id
        self.hero_image = self.kwargs['hero_image']

        if self.save(verbose=False):
            self.logger.warn('Created post! %s' % self)
        else:
            raise AttributeError('New post record could not be saved!')


    def serialize(self):
        """ Returns a fancy version of a post. """

        # expand the hero image
        output = copy(self.record)
        output['hero_image'] = images.expand_image(output['hero_image'])

        # loop through attachment oids and expand
        if getattr(self, 'attachments', None) is not None:
            output['attachments'] = []
            for attachment_oid in self.attachments:
                output['attachments'].append(images.expand_image(attachment_oid))

        # now, create some HTML from the plaintext
        output['html_lede'] = util.fancy_html(output.get('lede', ''))
        output['html_body'] = util.fancy_html(output.get('body', ''))

        return output


    def update(self):
        """ Calls the parent class update() method, then does some additional
        stuff required by the post object. """

        was_published = getattr(self, 'published', False)

        # manage the attachments/tags/list (of OIDs) before update/save
        for attrib in ['attachments', 'tags']:
            if flask.request.json.get(attrib, None) is not None:
                setattr(
                    self,
                    attrib,
                    list(set(
                        [
                            ObjectId(a["$oid"]) for
                            a in flask.request.json[attrib]
                    ]
                    ))
                )
                del flask.request.json[attrib]

        super().update(verbose=False)

        if not was_published and self.published:
            self.published_on = datetime.now()
        elif was_published and not getattr(self, 'published', False):
            self.published_on = None


        self.save()


    def save(self, verbose=True):
        """ Calls the base class method after creating the handle. """

        date_str = self.created_on.strftime(util.YMDHMS)
        self.handle = util.string_to_handle(date_str + ' ' + self.title)
        return super().save(verbose)
