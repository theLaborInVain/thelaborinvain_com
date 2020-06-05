"""

    This is the main routes.py file for the main page blog app.

"""

# standard library
import json
import os

# second party
import bson
from bson.objectid import ObjectId
from bson import json_util
import flask
import flask_login
from werkzeug.urls import url_parse

# application imports
from app import app, models, util
from app.models import figures as WhatTheLiteralFuck
from app.models import posts
from app.forms import LoginForm

#
#   start the insanity
#

@app.route('/', methods=['GET','POST'])
def index():
    """ Get posts, show posts. """
    return flask.render_template(
        'blog.html',
        keywords = ", ".join(app.config['KEYWORDS']),
        og=util.og_default,
        **app.config
    )


@app.route('/rss.xml')
@app.route('/rss/<feed_type>')
@app.route('/f/<feed_type>')
def get_rss_feed(feed_type=None):
    """ Our routes for RSS. """
    if feed_type is None:
        feed_type = 'posts'

    if feed_type != 'posts':
        return flask.Response(
            response="Feed type '%s' not found!" % feed_type,
            status=404
        )

    return flask.Response(
        response=posts.get_feed(),
        status=200,
        mimetype='application/atom+xml',
    )

@app.route('/sitemap.xml')
def get_sitemap():
    """ Turns posts into a sitemap."""

    return flask.Response(
        response=posts.get_sitemap(),
        status=200,
        mimetype='application/atom+xml',
    )


@app.route('/b/<post_handle>')
def get_one_post(post_handle):
    """ Get one post with the hande 'post_handle'. Return it. """
    post = app.config['MDB'].posts.find_one({'handle': post_handle})
    if post is None:
        return flask.Response(response='Post not found!', status=404)

    post_object=posts.Post(_id=post['_id'])

    return flask.render_template(
        'post.html',
        keywords = post_object.get_keywords_string(),
        og = post_object.get_og_dict(),
        post_object = post_object,
        **app.config
    )


@app.route('/search/<target_collection>')
def search_collection(target_collection):
    """ Searches posts for posts with a tag. URL should be like this:
            /search/posts?tag=Munchkin (or similar)
    """

    if target_collection != 'posts':
        return flask.Response(response='Not implemented!', status=501)

    if flask.request.args.get('tag', None) is None:
        return flask.Response(response='Tag param is required!', status=400)

    # get the tag's object or return None
    tag_obj = app.config['MDB'].tags.find_one({
        'name': flask.request.args.get('tag')
    })
    if tag_obj is None:
        return flask.Response(
            response={},
            status=200,
            mimetype='application/json'
        )

    results = app.config['MDB'].posts.find({
        'tags': {
            '$in': [tag_obj['_id']]
        }
    })
    return flask.Response(
        response=json.dumps([
            posts.Post(_id=post_rec['_id']).serialize() for post_rec in
            results
        ], default=json_util.default),
        status=200,
        mimetype='application/json'
    )


@app.route('/get/<collection>')
def get_assets(collection):
    """ Get JSON of 'collection' assets."""

    params = flask.request.args
    count = int(params.get('count', app.config['GET_COUNT_DEFAULT']))

    results = app.config['MDB'][collection].find().sort([
        ('last_used_on', -1),
        ('created_on', -1)
    ]).limit(count)

    # if we're here for posts, use the special helper to get fancy posts
    if collection == "posts":
        results = posts.get(count)

    if collection == 'tags':
        results.sort('name')

    return flask.Response(
        response=json.dumps([r for r in results], default=json_util.default),
        status=200,
        mimetype='application/json'
    )


@app.route('/<action>/<collection>/<oid>')
def get_asset(action, collection, oid):
    """ Generic public, non-auth asset retrieval """

    # attachments are special, they key off of a post
    if action == 'get' and collection == 'attachments':
        attachments = app.config['MDB'].attachments.find(
            {'post_id': ObjectId(oid)}
        )
        output = []
        for attachment in attachments:
            output.append(posts.Attachment(_id=attachment['_id']).serialize())
        return flask.Response(
            response=json.dumps(
                output,
                default=json_util.default
            ),
            status=200,
            mimetype='application/json'
        )

    try:
        asset_object = models.get_asset(collection, ObjectId(oid))
    except bson.errors.InvalidId:
        return flask.Response(
            response="'%s' is not a valid Object ID!" % oid,
            status=404
        )

    return flask.Response(
        response=json.dumps(
            asset_object.serialize(),
            default=json_util.default
        ),
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

        def fail():
            flask.flash("Invalid username or password")
            return flask.redirect(flask.url_for('login'))

        try:
            user_obj = models.User(email=form.email.data)
        except Exception as e:  # unknown user
            return fail()

        if not user_obj.check_password(form.password.data):
            return fail()
        else:
            # success--log the user in!
            user_obj.logger.info('User authenticated! %s' % user_obj)
            flask_login.login_user(user_obj, remember=form.remember_me.data)
            next_page = flask.request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = flask.url_for('admin')
            return flask.redirect(next_page)

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
@app.route('/create/<asset_type>', methods=['POST'])
def create_asset(asset_type):
    """ Creates a new 'asset_type'. Returns a 200 and the oid. """

    params = flask.request.json

    asset_object = models.get_asset(asset_type, **params)

    return flask.Response(
        response=json.dumps(
            {'_id': asset_object._id},
            default=json_util.default
        ),
        status=200,
        mimetype='application/json'
    )


@flask_login.login_required
@app.route('/update/<asset_type>/<asset_oid>', methods=['POST'])
def update_asset(asset_type, asset_oid):
    """ Pulls the asset, calls the update method. """
    asset_object = models.get_asset(asset_type, ObjectId(asset_oid))
    asset_object.update()
    return flask.Response(
        response=json.dumps(asset_object.serialize(), default=json_util.default),
        status=200,
        mimetype='application/json',
    )


@flask_login.login_required
@app.route('/edit_post/<post_oid>', methods=['GET', 'POST'])
def edit_post(post_oid):
    """ Pulls a post for editing in the webapp. """

    # first, make sure we can even get a post to edit
    post_object = posts.Post(_id=ObjectId(post_oid))

    # the GET is for editing in the webapp; the POST 
    # is for updating MDB
    if flask.request.method == 'GET':
        if not flask_login.current_user.is_authenticated:
            return flask.redirect(flask.url_for('admin'))
        return flask.render_template(
            'admin_edit.html',
            post=post_object.serialize(),
            **app.config
            )
    else:   # if flesk.request.method == 'POST'
        post_object.update()
        return flask.Response(
            response=json.dumps(
                post_object.serialize(),
                default=json_util.default
            ),
            status=200,
            mimetype='application/json',
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
            image_obj = models.images.Image(raw_upload=in_file)
            processed += 1

    msg = "Uploaded %s files successfully!" % processed
    return flask.redirect(flask.url_for('admin'))




#
#   customize some of the flask built-ins here
#

@app.errorhandler(util.InvalidUsage)
def return_exception(exception):
    """ errorhandler is a built-in; we're using it to return an exception object
    as a string, e.g. so browsers and whatever can see it. """
    return flask.Response(response=exception.msg, status=exception.status_code)


@app.context_processor
def inject_template_scope():
    """ Injects the consent cookie into scope. """
    injections = dict()

    def cookies_check():
        value = flask.request.cookies.get('cookie_consent')
        return value == 'true'

    injections.update(cookies_check=cookies_check)

    return injections
