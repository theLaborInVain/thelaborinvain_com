'''

    Application init happens here; we add middleware and logging.

'''

# second party imports
import flask

# application imports
from config import Config

# EB looks for an 'application' callable by default.
application = flask.Flask(__name__)
application.config.from_object(Config())

from app import routes
