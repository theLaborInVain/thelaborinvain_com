"""

    This is where we initialize the app. Try to keep it clean, OK?

"""

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

login = LoginManager(app)
login.login_view = 'login'

# sorry, pep8

from app import routes
