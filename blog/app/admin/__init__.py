"""

    The actual Administration module methods live here.

    See __main__.py in this folder for things you can do via admin.sh

"""

# standard lib imports
import os

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

    def dump_users(self):
        """ Dumps all user records. """
        return app.config['MDB'].users.find()


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

