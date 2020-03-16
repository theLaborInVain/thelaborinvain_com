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
import pymongo

# application imports
from app import app, models, util
from app.models import images, figures

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


def get_sitemap():
    """ Renders all published posts as a sitemap.xml file for GOOGOO. """

    sitemap = ET.Element('urlset')
    sitemap.set('xmlns', "http://www.sitemaps.org/schemas/sitemap/0.9")

    root_url = ET.SubElement(sitemap, 'url')
    ET.SubElement(root_url, 'loc').text = app.config['URL'] + '/'
    ET.SubElement(root_url, 'changefreq').text = 'daily'
    ET.SubElement(root_url, 'priority').text = '0.8'

    # set lastmod for root URL based on latest post
    latest_post = app.config['MDB'].posts.find_one({
        'published': {'$exists': True},
        },
        sort=[( 'published_on', pymongo.DESCENDING )]
    )

    root_url_lastmod = latest_post['published_on'].strftime(util.YMD)
    ET.SubElement(root_url, 'lastmod').text = root_url_lastmod

    for rec in app.config['MDB'].posts.find({
        'published': {'$exists': True},
        'published_on': {'$exists': True},
    }).sort('published_on', -1):
        # get post
        post_object = Post(_id=rec['_id'])

        # set values
        url_item = ET.SubElement(sitemap, 'url')
        ET.SubElement(url_item, 'loc').text = post_object.get_url()

        updated_on = getattr(post_object, 'updated_on', None)
        if updated_on is None:
            updated_on = post_object.created_on
        ET.SubElement(url_item, 'lastmod').text = updated_on.strftime(util.YMD)
        ET.SubElement(url_item, 'changefreq').text = 'never'


    return ET.tostring(sitemap)


def get_feed():
    """ Returns XML for RSS feed. """

#    logger = util.get_logger(log_name='rss')

    feed = ET.Element('feed')
    feed.set('xmlns', 'http://www.w3.org/2005/Atom')
    feed.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
    feed.set('xmlns:webfeeds', 'http://webfeeds.org/rss/1.0')

    feed_atom_link = ET.SubElement(feed, 'link')
    feed_atom_link.set('rel','self')
    feed_atom_link.set('href', flask.request.url)
    feed_atom_link.set('type', 'application/atom+xml')

    ET.SubElement(feed, 'title').text = app.config['TITLE']
    ET.SubElement(feed, 'id').text = app.config['URL'] + "/"
#    ET.SubElement(feed, 'link').set('href', app.config['URL'])
    ET.SubElement(feed, 'updated').text = get_latest_post().published_on.isoformat("T") + "Z"
    ET.SubElement(feed, 'category').set('term', 'miniature painting')
    ET.SubElement(feed, 'category').set('term', 'tabletop gaming')
    ET.SubElement(feed, 'category').set('term', 'hobby')

    rights = ET.SubElement(feed, 'rights')
    rights.text = app.config['COPYRIGHT']
    rights.set('type', 'html')

    # author email
    feed_author = ET.SubElement(feed, 'author')
    ET.SubElement(feed_author, 'name').text = app.config['ADMIN_NAME']
    ET.SubElement(feed_author, 'email').text = app.config['ADMIN_EMAIL']

    # logo/icon
    ET.SubElement(feed, 'logo').text = \
        app.config['URL'] + '/static/media/the_labor_in_vain_logo-01.png'
    ET.SubElement(feed, 'webfeeds:cover').text = \
        app.config['URL'] + '/static/media/the_labor_in_vain_logo-01.png'
    ET.SubElement(feed, 'icon').text = \
        app.config['URL'] + '/static/media/favicon.ico'
    ET.SubElement(feed, 'webfeeds:icon').text = \
        app.config['URL'] + '/static/media/favicon.ico'

    # misc.
    feed_anal = ET.SubElement(feed, 'webfeeds:analytics')
    feed_anal.set('id', 'UA-88194596-3')
    feed_anal.set('engine', 'GoogleAnalytics')

    # create entries here
    for rec in app.config['MDB'].posts.find({
        'published': {'$exists': True},
        'published_on': {'$exists': True},
    }).sort('published_on', -1).limit(10):
        # get post
        post = Post(_id=rec['_id']).serialize()
        post_url = app.config['URL'] + '/b/' + post['handle']
        hero_img_url = app.config['URL'] + '/images/' + post['hero_image']['base_name']

        # start it up!
        post_item = ET.SubElement(feed, 'entry')

        # required author block
        author = ET.SubElement(post_item, 'author')
        ET.SubElement(author, 'name').text = post['author']['name']
        ET.SubElement(author, 'email').text = post['author']['email']

        # thumbnail
        thumbnail = ET.SubElement(post_item, 'media:thumbnail')
        thumbnail.set('xmlns:media', 'http://search.yahoo.com/mrss/')
        thumbnail.set('url', hero_img_url)
        thumbnail.set('height', '72')
        thumbnail.set('weight', '72')

        # required post content
        post_content = ET.SubElement(post_item, 'content')
        post_content.text = \
            post['html_hero_image'] + post['html_lede'] \
            + post['html_body'] + '<hr/>' + post['html_attachments']
        post_content.set('type','html')
        link = ET.SubElement(post_item, 'link')
        link.set('href', post_url)
        ET.SubElement(post_item, 'id').text = post_url
        post_summary = ET.SubElement(post_item, 'summary')
        post_summary.text = post['html_lede']
        post_summary.set('type','html')

        # recommended for post
        for tag in post['tag_dictionary']:
            ET.SubElement(post_item, 'category').set('term', tag['name'])
        ET.SubElement(post_item, 'title').text = post['title']
        ET.SubElement(post_item, 'published').text = \
            post['published_on'].isoformat("T") + "Z"
        ET.SubElement(post_item, 'updated').text = \
            post['published_on'].isoformat("T") + "Z"

    return ET.tostring(feed)


class Tag(models.Model):
    """ Tags are very simple little guys. """

    def __init__(self, *args, **kwargs):

        models.Model.__init__(self,  *args, **kwargs)
        self.collection = 'tags'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            'name': str,
            'last_used_on': datetime,
        }
        self.required_attribs = ['name']

        self.load()


class Paint(models.Model):
    """ Paints are sort of like tags, in that they're attached to posts, but
    they contain a little more data. """

    def __init__(self, *args, **kwargs):
        """ Initialize a Paint object. """
        models.Model.__init__(self,  *args, **kwargs)

        self.collection = 'paints'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            'name': str,
            'manufacturer': str,
            'url': str,
            'colors': list,
            'gradient': str,
            'last_used_on': datetime,
            'ink': bool,
            'shader': bool,
            'metallic': bool,
            'primer': bool,
        }
        self.required_attribs = ['name', 'manufacturer', 'colors']

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
        current_attachments = self.mdb.find({'post_id': ObjectId(self.post_id)})
        self.sort_order = current_attachments.count() + 1
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
            'paints': list,
            'figure': ObjectId,
            'hero_image': ObjectId,
            'hero_caption': str,        # just a string

            # meta
            'created_by': ObjectId,
            'created_on': datetime,
            'updated_on': datetime,
            'published_on': datetime,
            'published': bool,
        }

        self.required_attribs = [
            'figure',
            'hero_image',
        ]

        self.load()


    def new(self):
        """ Loads the figure, """

        if self.kwargs.get('figure', None) is None:
            raise ValueError("'figure' attribute is required!")

        # get the figure, use it to set a few things
        figure_object = figures.Figure(_id=self.kwargs['figure'])

        # set the post title and hero caption
        self.title = getattr(figure_object, 'name')
        publisher = getattr(figure_object, 'publisher', '')
        self.hero_caption = publisher + ': ' + self.title

        # finally, use the figure's tags for the post
        self.tags = getattr(figure_object, 'tags', [])

        super().new()


    def serialize(self):
        """ Returns a fancy version of a post. """

        # expand the hero image
        output = copy(self.record)
        try:
            output['hero_image'] = images.expand_image(output['hero_image'])
        except KeyError:
            output['hero_image'] = {'base_name': 'unknown_image.jpg'}

        output['html_hero_image'] = \
            '<img class="webfeedsFeaturedVisual" src="%s/images/%s" />' % (
                app.config['URL'],
                output['hero_image']['base_name']
            )

        # loop through attachment oids and expand
        output['attachments'] = []
        output['html_attachments'] = ""
        attachment_records = app.config['MDB'].attachments.find({
            'post_id': self._id
        })
        if attachment_records is not None:
            for a_rec in attachment_records:
                a_rec['image'] = images.expand_image(a_rec['image_id'])
                output['attachments'].append(a_rec)
                stub = '<img src="%s/images/%s" />'
                output['html_attachments'] += stub % (
                    app.config['URL'], a_rec['image']['base_name']
                )

        # now, create some HTML from the plaintext
        output['html_lede'] = util.fancy_html(output.get('lede', ''))
        output['html_body'] = util.fancy_html(output.get('body', ''))


        output['author'] = dict(self.get_author())
        output['tag_dictionary'] = list(self.get_tags())

        return output


    def update(self):
        """ Calls the parent class update() method, then does some additional
        stuff required by the post object. """

        was_published = getattr(self, 'published', False)

        # manage the attachments/tags/list (of OIDs) before update/save
        for attrib in ['attachments', 'tags', 'paints']:
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

                # log tag and paint usage
                if attrib in ['tags', 'paints']:
                    for a_dict in flask.request.json[attrib]:
                        a_object = models.get_asset(attrib, _id=a_dict['$oid'])
#                        a_object = Tag(_id=tag_dict['$oid'])
                        a_object.set_last_used_on()

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
        try:
            return app.config['MDB'].users.find_one({'_id': self.created_by})
        except AttributeError:
            return {'name': None, 'email': None}


    def get_keywords_string(self):
        """ Creates a string representing keywords (for use in server-side meta
        data rendering. """

        keywords_list = copy(app.config['KEYWORDS'])
        keywords_list.extend(self.get_tags(str))
        keywords_list.append('painted')
        return ", ".join(keywords_list)


    def get_og_dict(self):
        """ Creates a dictionary of Open Graph tags. """

        og = copy(util.og_default)

        hero_image_obj = images.expand_image(self.hero_image)
        og['image'] = os.path.join(
            app.config['URL'],
            'images',
            hero_image_obj['base_name']
        )

        og['title'] = "The Labor in Vain: '%s'" % self.title
        if getattr(self, 'figure', None) is not None:
            figure = figures.Figure(_id=self.figure)
            og['title'] += ' by %s' % figure.publisher

        og_desc = self.hero_caption + " Painted by %s" % self.get_author()['name']
        og['description'] = og_desc

        og['url'] = os.path.join(app.config['URL'], 'b/', self.handle)

#        og['type'] = 'blog'
        og['type'] = "instapp:photo"
        og['published_time'] = self.published_on.isoformat()

        return og


    def get_tags(self, return_type=object):
        """ Returns a list of tag OBJECTS unless otherwise specified. """
        if not hasattr(self, 'tags') or self.tags is None:
            return []

        post_tags = app.config['MDB'].tags.find(
            {'_id': {'$in': self.tags}}
        ).sort('name')

        if return_type == str:
            return [t['name'] for t in post_tags]

        return post_tags

    def get_url(self):
        """ Returns the URL of the post. """
        return app.config['URL'] + '/b/' + self.handle
