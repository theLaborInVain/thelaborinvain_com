"""
    The Post model lives here (at the bottom).

    Up top, we've got helper methods for working with posts.

"""

# standard lib
from datetime import datetime
from copy import copy

# second party imports
import flask
from bson.objectid import ObjectId

# application imports
from app import app, models
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
        }

        self.required_attribs = [
            'image_id',
            'post_id',
        ]

        self.load()



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
            'body': str,
            'tags': list,
            'hero_image': ObjectId,
            'hero_caption': str,        # just a string
            'attachments': list,        # list of image oids
            'captions': list,           # list of dictionaries

            # meta
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

        return output


    def update(self):
        """ Calls the parent class update() method, then does some additional
        stuff required by the post object. """

        was_published = getattr(self, 'published', False)

        # manage the attachments list (of OIDs) before update/save
        if flask.request.json.get('attachments', None) is not None:
            self.logger.warn(flask.request.json)
            setattr(
                self,
                'attachments',
                list(set(
                    [
                        ObjectId(a['_id']["$oid"]) for
                        a in flask.request.json['attachments']
                    ]
                ))
            )
            del flask.request.json['attachments']

        super().update(verbose=False)

        if not was_published and self.published:
            self.published_on = datetime.now()
        elif was_published and not getattr(self, 'published', False):
            self.published_on = None


        self.save()


