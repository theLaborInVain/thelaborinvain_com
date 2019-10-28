"""
    The Post model lives here (at the bottom).

    Up top, we've got helper methods for working with posts.

"""

# standard lib
from copy import copy
from datetime import datetime
from email.utils import formatdate
import os
import xml.etree.ElementTree as ET

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


def get_latest_post():
    """ Laziness function to return the latest post. """
    post_record = app.config['MDB'].posts.find_one(
        {'published': True, 'published_on': {'$exists': True}},
        sort=[('published_on', -1)]
    )
    return Post(_id=post_record['_id'])


def get_feed():
    """ Returns XML for RSS feed. """

    logger = util.get_logger(log_name='rss')

    feed = ET.Element('feed')
    feed.append(
        ET.Comment('RSS generated by v.%s of TLV blog.' % app.config['VERSION'])
    )
    feed.set('version', '1.0')
    feed.set('xmlns', 'http://www.w3.org/2005/Atom')

    ET.SubElement(feed, 'title').text = app.config['TITLE']
    ET.SubElement(feed, 'id').text = app.config['URL']
    ET.SubElement(feed, 'link').text = app.config['URL']
    ET.SubElement(feed, 'updated').text = \
        formatdate(
            float(get_latest_post().published_on.strftime('%s'))
        )
    ET.SubElement(feed, 'category').set('term', 'miniature painting')
    ET.SubElement(feed, 'category').set('term', 'tabletop gaming')
    ET.SubElement(feed, 'category').set('term', 'hobby')

    rights = ET.SubElement(feed, 'rights')
    rights.text = app.config['COPYRIGHT']
    rights.set('type', 'html')

    # author email
    ET.SubElement(
        ET.SubElement(feed, 'author'),
        'email'
    ).text = app.config['ADMIN_EMAIL']

    ET.SubElement(feed, 'logo').text = (
        'https://blog.thelaborinvain.com/static/media/'
        'the_labor_in_vain_logo_no_text.webp'
    )


    # create entries here
    for rec in app.config['MDB'].posts.find({
        'published': {'$exists': True},
        'published_on': {'$exists': True},
    }).sort('published_on', -1).limit(3):
        # get post
        post = Post(_id=rec['_id']).serialize()
        post_item = ET.SubElement(feed, 'entry')

        # required author block
        author = ET.SubElement(post_item, 'author')
        ET.SubElement(author, 'name').text = post['author']['name']
        ET.SubElement(author, 'email').text = post['author']['email']

        # required post content
        ET.SubElement(post_item, 'content').text = \
            post['html_lede'] + post['html_body']
        link = ET.SubElement(post_item, 'link')
        link.set('href', app.config['URL'] + '/b/' + post['handle'])
        ET.SubElement(post_item, 'summary').text = post['html_lede']

        # recommended for post
        for tag in post['tag_dictionary']:
            ET.SubElement(post_item, 'category').set('term', tag['name'])
        ET.SubElement(post_item, 'title').text = post['title']
        ET.SubElement(post_item, 'published').text = \
            formatdate(float(post['published_on'].strftime('%s')))
        post_rights = ET.SubElement(feed, 'rights')
        post_rights.text = app.config['COPYRIGHT']
        post_rights.set('type', 'html')

    return ET.tostring(feed)


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

        output['author'] = self.get_author()
        output['tag_dictionary'] = self.get_tags()

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



    def get_author(self):
        """ Gets the post's author record from users. """
        return app.config['MDB'].users.find_one({'_id': self.created_by})

    def get_tags(self):
        """ Returns a dictionary of tags. """
        return app.config['MDB'].tags.find({'_id': {'$in': self.tags}}).sort('name')
