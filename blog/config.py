"""

    Rather than using ConfigParser and using a text file, we do settings here,
    so that when we change them while working on the app, the dev server
    restarts.

"""

# standard lib
import os
import secrets

# second party
from pymongo import MongoClient


class Config(object):
    VERSION = "0.11.62"
    PORT = 8060
#    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECRET_KEY = secrets.token_hex(16)
    MDB = MongoClient()['thelaborinvain_blog_v0']
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    GET_COUNT_DEFAULT = 9999
