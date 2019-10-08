"""
    The Post model lives here (at the bottom).

    Up top, we've got helper methods for working with posts.

"""

# standard lib
from datetime import datetime

# second party imports
from bson.objectid import ObjectId

# application imports
from app import app, models


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
        post['hero_image'] = app.config['MDB'].images.find_one(
            {'_id': post['hero_image']}
        )
        output.append(post)

    return output


class Post(models.Model):
    """ Posts are complex objects and this is their base class. Their various
    types are objects that use this model as their base. """

    def __init__(self, *args, **kwargs):

        models.Model.__init__(self,  *args, **kwargs)
        self.collection = 'posts'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            'title': str,
            'hero_image': ObjectId,
            'created_on': datetime,
            'updated_on': datetime,
        }

        self.load()

    def __repr__(self):
        return '<Post {}>'.format(self.title)


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
