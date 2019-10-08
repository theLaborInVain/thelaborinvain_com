"""

    This is the main routes.py file for the main page blog app.

"""

# standard library
import json
import os

# second party
from bson.objectid import ObjectId
from bson import json_util
import flask
import flask_login

# application imports
from app import app, models, util
from app.models import posts
from app.forms import LoginForm

#
#   start the insanity
#

@app.route('/', methods=['GET','POST'])
def index():
    """ Get posts, show posts. """
    return flask.render_template('blog.html', posts=posts.get())


@app.route('/get/<collection>')
def get_assets(collection):
    """ Get JSON of 'collection' assets."""

    try:
        count = int(flask.request.args.get('count', default=10))
    except:
        count = 10

    results = app.config['MDB'][collection].find().sort(
        'created_on', -1
    ).limit(count)

    # if we're here for posts, use the special helper to get fancy posts
    if collection == "posts":
        results = posts.get(count)

    return flask.Response(
        response=json.dumps([r for r in results], default=json_util.default),
        status=200,
        mimetype='application/json'
    )


@app.route('/static/<sub_dir>/<path:path>')
def route_to_static(path, sub_dir):
    """ The webserver will do this when deployed; this is for dev. """
    static_dir = os.path.join(app.root_path, '..', 'static/', sub_dir)
    return flask.send_from_directory(static_dir, path)


@app.route('/images/<path:path>')
def route_to_images(path):
    """ The webserver will do this when deployed; this is for dev. """
    uploads_dir = os.path.join(app.root_path, '..', 'uploads/')
    return flask.send_from_directory(uploads_dir, path)





#
#   ADMIN routes
#


#   login/logout public routes

@app.route('/login', methods=['GET','POST'])
def login():
    """ We handle admin panel logins here. """

    form = LoginForm()
    if form.validate_on_submit():
        user_rec = app.config['MDB'].users.find_one({'email': form.email.data})
        if user_rec is not None:
            user_obj = models.User(_id=user_rec['_id'])
            if user_obj.check_password(form.password.data):
                flask_login.login_user(user_obj, remember=form.remember_me.data)
                return flask.redirect(flask.url_for('admin'))

        flask.flash("Invalid username or password")
        return flask.redirect(flask.url_for('login'))

    return flask.render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """ Logs the admin out; redirects to index. """
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))


#   private routes below

@app.route('/admin')
@flask_login.login_required
def admin():
    """ The main admin panel/controls; mostly we use this as a place for url_for
    redirects to point at. """
    return flask.render_template('admin_menu.html', **app.config)


@flask_login.login_required
@app.route('/create_post', methods=['POST'])
def create_post():
    """ Creates a new POST. Returns a 200 and the oid. """
    params = flask.request.json
    post_object = posts.Post(
        title=params['title'], hero_image=ObjectId(params['hero_image'])
    )
    return flask.Response(
        response=json.dumps(
            {'_id': post_object._id},
            default=json_util.default
        ),
        status=200,
        mimetype='application/json'
    )


@flask_login.login_required
@app.route('/rm/<collection>/<asset_oid>', methods=['GET'])
def rm_one_asset(collection, asset_oid):
    """ Removes a single asset. """

    asset_object = models.get_asset(collection, ObjectId(asset_oid))
    asset_object.delete()
    return flask.redirect(flask.url_for('admin'))


@app.route('/upload', methods=['POST', 'GET'])
@flask_login.login_required
def upload_file():
    """ Accepts a post containing a file, parks it in uploads. """

    # redirect to admin it NOT a post
    if flask.request.method == 'GET':
        return flask.redirect(flask.url_for('admin'))

    logger = util.get_logger(log_name='upload')

    def allowed_file(filename):
        """ private method to check file names for ext. """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() \
            in app.config['ALLOWED_EXTENSIONS']

    processed = 0
    for in_file in flask.request.files.getlist('file[]'):
        if allowed_file(in_file.filename):
            image_obj = models.Image(raw_upload=in_file)
            processed += 1

    msg = "Uploaded %s files successfully!" % processed
    return flask.redirect(flask.url_for('admin'))

