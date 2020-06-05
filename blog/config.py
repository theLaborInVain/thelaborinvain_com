"""

    Rather than using ConfigParser and using a text file, we do settings here,
    so that when we change them while working on the app, the dev server
    restarts.

"""

# standard lib
from datetime import datetime
import os
import sys

# second party
from pymongo import MongoClient
from bson.objectid import ObjectId

class Config(object):
    URL = 'https://blog.thelaborinvain.com'
    IMAGE = URL + '/static/media/the_labor_in_vain_logo_no_text.webp'
    TITLE = 'The Labor in Vain'
    DESC = (
        'Miniatures, Hobby and Projects Blog for The Labor in Vain, '
        'a production company based in Chicago, IL.'
    )
    COPYRIGHT = (
        '&copy; 2018 - %s, The Labor in vain. All content published on this '
        'website, to include text, photos, video and other media, are the '
        'property of The Labor in Vain and may not be reproduced for '
        'commercial purposes without consent.'
    ) % datetime.now().strftime('%Y')
    KEYWORDS = ['miniatures', 'miniatures painting', 'minis']
    ADMIN_NAME = "Timothy O'Connell"
    ADMIN_EMAIL = 'toconnell@thelaborinvain.com'
    VERSION = "0.37.191"
    PORT = 8060
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(sys.path)
#    SECRET_KEY = secrets.token_hex(16)  # this breaks the login cookie
    MDB = MongoClient()['thelaborinvain_blog_v0']
    CANONICAL_TAG_NAME = 'Finished pieces'
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    GET_COUNT_DEFAULT = 9999

    if os.environ.get('FLASK_ENV') == 'production':
        SESSION_COOKIE_SECURE = True
        REMEMBER_COOKIE_SECURE = True
