"""

    The actual Administration module methods live here.

    See __main__.py in this folder for things you can do via admin.sh

"""

# standard lib imports
import os

# second party imports
from bson.objectid import ObjectId

# application imports
from app import app, models, util


class AdministrationObject():
    """ The AdministrationObject class definition. """

    def __init__(self):
        self.logger = util.get_logger()


    #
    #   CRUD methods
    #

    def add_user(self, name=None, email=None, password=None):
        """ Adds a new user to MDB using the model method. Returns it. """
        return models.User(name=name, email=email, password=password)

    #
    #   GET/SET methods
    #

    def get_collection(self, collection):
        """ Dumps all user records. """
        return app.config['MDB'][collection].find()


    def set_attribute(self, collection=None, asset_oid=None,
        attrib=None, value=None):
        """ Updates an arbitrary asset. Be careful with this!"""

        asset_record = app.config['MDB'][collection].find_one({
            '_id': ObjectId(asset_oid)
        })
        if asset_record is None:
            raise ValueError('Asset not found! %s' % ObjectId(asset_oid))

        asset_record[attrib] = value

        app.config['MDB'][collection].save(asset_record)
        return asset_record


    def initialize(self):
        """ Purges all posts and images from the DB and filesystem. """

        print(" - Initializing MDB collections!")
        collections = ['posts','images','attachments','tags']
        for collection in collections:
            removed = app.config['MDB'][collection].remove()
            print("  Removed %s records from %s.%s" % (
                removed['n'],
                app.config['MDB'].name,
                collection,
                )
            )

        print(" - Initializing Uploads folder!")
        for the_file in os.listdir(app.config['UPLOADS']):
            file_path = os.path.join(app.config['UPLOADS'], the_file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print("  Removed '%s'" % file_path)
            except Exception as e:
                raise


    def set_password(self, email=None, password=None):
        """ Sets a password. """
        user_record = app.config['MDB'].users.find_one({'email': email})
        user_object = models.User(_id=user_record['_id'])
        user_object.update_password(password)
        return True

