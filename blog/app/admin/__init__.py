"""

    The actual Administration module methods live here.

    See __main__.py in this folder for things you can do via admin.sh

"""

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

        app.config['MDB'].posts.remove()
        app.config['MDB'].images.remove()


