'''

    Routes here; object work hands of to brokerage methods.

'''

# second part
import flask

# application imports
from app import application

@application.route('/')
@application.route('/index')
def index():
    ''' Landing page; no auth. '''
    return flask.render_template('/index/_base.html', **application.config)


# for dev only; we have EB routes for statics in prod
@application.route('/static/<sub_dir>/<path:path>')
def route_to_static(path, sub_dir):
    """ Returns the static dir when working in dev. """
    return flask.send_from_directory("static/%s" % sub_dir, path)
