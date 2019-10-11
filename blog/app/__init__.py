"""

    This is where we initialize the app. Try to keep it clean, OK?

"""
# standard lib
import os

# second party
from flask import Flask
from flask_login import LoginManager
import pymongo

# app imports
from config import Config


#
#   import the app and set its config stuff; then import the login mgr
#

app = Flask(__name__)
app.config.from_object(Config)
app.config['MDB'].users.create_index([('email', pymongo.TEXT),], unique=True)
app.config['MDB'].tags.create_index([('name', pymongo.TEXT),], unique=True)
app.config['UPLOADS'] = os.path.join(app.root_path, '..', 'uploads/')

login = LoginManager(app)
login.login_view = 'login'

# sorry, pep8

from app import routes
