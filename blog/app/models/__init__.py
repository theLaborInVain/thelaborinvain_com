"""

	Model base class/object definitions live here!

"""

# standard library
from bson.objectid import ObjectId
from datetime import datetime
from hashlib import md5
import os

# second party
import flask
import flask_login
import pymongo
from werkzeug.security import safe_str_cmp, generate_password_hash, \
    check_password_hash

# application imports
from app import app, login, models, util

#
#   Flask login manager
#

@login.user_loader
def load_user(_id):
    return User(_id=ObjectId(_id))


#
#   helpers
#

def get_asset(collection=None, _id=None, **params):
    """ Gets an asset from a collection, returns it. """

    if collection == 'images':
        return models.images.Image(_id=_id)
    elif collection == 'posts':
        return models.posts.Post(_id=_id)
    elif collection == 'post':
        return models.posts.Post(_id=_id)
    elif collection == 'attachment':
        return models.posts.Attachment(_id=_id, **params)
    elif collection == 'attachments':
        return models.posts.Attachment(_id=_id, **params)
    elif collection == 'tag':
        return models.posts.Tag(_id=_id, **params)
    elif collection == 'tags':
        return models.posts.Tag(_id=_id, **params)

    raise ValueError('get_asset() is not supported for %s yet!' % collection)


#
#   object classe   object classess
#


class Model(object):
    """ The base class for all models. """


    def __init__(self, *args, **kwargs):
        """ Default init for all objects. """

        self.logger = util.get_logger()
        self.kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)


    def __repr__(self):
        return '<%s %s>' % (self.collection, self._id)


    def new(self):
        """ Adds a new record to MDB. """

        # sanity check
        for req_var in self.required_attribs:
            if req_var not in self.kwargs:
                err = "The '%s' kwarg is required when creating new %s!"
                self.logger.error(self.kwargs)
                raise ValueError(err % (req_var, self.collection))

        # do it
        self.logger.warn('Creating new %s record!' % self.collection)

        for req_var in self.required_attribs:
            setattr(self, req_var, self.kwargs[req_var])
        self.created_on = datetime.now()
        self._id = self.mdb.insert({})

        try:
            self.save()
        except pymongo.errors.DuplicateKeyError as e:
            self.mdb.remove({'_id': self._id})
            self.logger.error(e)
            self.logger.error('Cannot create asset: %s' % self)
            raise ValueError('Duplicate key error prevented asset creation!')


    def load(self):
        """ Call this from the subclass objects: it uses self.whatever vars that
        come from their __init__() methods. """

        if '_id' in self.kwargs and self.kwargs['_id'] is not None:
            self._id = self.kwargs.get('_id')
        else:
            self.new()  #sets self._id

        # sanity check

        self.record = self.mdb.find_one({'_id': self._id})
        if self.record is None:
            raise ValueError('Record OID %s not found in MDB!' % self._id)

        for key, value in self.record.items():
            setattr(self, key, value)


    def save(self, verbose=app.config['DEBUG']):
        """ Saves the object's self.data_model attribs to its self.collection
        in the MDB. """

        # sanity check
        if not hasattr(self, '_id'):
            err = "'%s.%s' record requires '_id' attrib to save!"
            raise AttributeError(
                err % (app.config['MDB'].name, self.collection)
            )

        # make a record, enforce the data model
        record = {'_id': self._id}
        for key, value_type in self.data_model.items():
            record[key] = getattr(self, key, None)
            if record[key] != None:
                try:
                    if not isinstance(record[key], value_type):
                        try:
                            record[key] = value_type(record[key])
                        except:
                            msg = "Could not cast value '%s' to %s type!"
                            raise TypeError(msg % (record[key], value_type))
                except TypeError as e:
                    self.logger.exception(e)
                    self.logger.error("Is '%s' a type, e.g. str?" % value_type)
                    self.logger.error('Did you add parens? Do not add parens.')
                    raise

        # save and, if verbose, log about it

        # set self.update_on, created_by, because most models support it
        self.updated_on = datetime.now()
        self.created_by = flask_login.current_user._id

        self.mdb.save(record)
        if verbose:
            self.logger.info('Saved changes to %s' % self)
        return True


    def serialize(self):
        """ Returns the object's record. """
        return self.record


    def update(self, verbose=True):
        """ Uses flask.request.json values to update an initialized object.
        Keys have to be in the self.data_model to be supported. """
        params = flask.request.json
        for key, value in params.items():
            if key in self.data_model.keys():

                # unfuck javascript-style date strings
                if self.data_model[key] == datetime:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.000Z')
                    except ValueError:
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            raise

                # set the self.attribute values
                setattr(self, key, value)

        self.save(verbose)


    def delete(self):
        """ Removes the record."""

        self.mdb.remove({'_id': self._id})
        self.logger.warn('Removed MDB record! %s' % self._id)
        return True

    #
    #   universal/general gets and sets
    #



class User(flask_login.UserMixin, Model):
    """ The user model. Hyper-simple: basically exists so the maintainers can
    sign in and create posts that link back to them. """

    def __init__(self, *args, **kwargs):

        """ Pass this an OID using the '_id' kwarg to load a user, otherwise,
        we expect that you're trying to create a new user. """

        Model.__init__(self,  *args, **kwargs)

        self.collection = 'users'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            'name': str,
            'email': str,
            'password': str,
            'created_on': datetime,
        }

        self.required_attribs = [
            'name',
            'email',
            'password'
        ]

        # try to set _id from email before we hand off to the base class
        # load() method.
        rec = self.mdb.find_one({'email': self.kwargs.get('email', None)})
        if rec is not None:
            self.kwargs['_id'] = rec['_id']

        self.load()


    def __repr__(self):
        return '<User {}>'.format(self.email)


    def get_id(self):
        """ Flask Login Manager uses this. Don't mess with it. """
        return str(self._id)




    #
    #   object-specific CRUD methods
    #

    def new(self):
        """ Adds a user to MDB; sets self._id on its way out. """

        for req_var in self.required_attribs:
            if req_var not in self.kwargs:
                err = "The '%s' kwarg is required when creating a new user!"
                self.logger.error(err % req_var)
                raise ValueError(err % req_var)

        self.logger.warn('Creating new user!')
        self.name = self.kwargs.get('name')
        self.email = self.kwargs.get('email').lower()
        self.created_on = datetime.now()

        try:
            self._id = self.mdb.insert({'email': self.email})
        except pymongo.errors.DuplicateKeyError:
            raise ValueError("Email '%s' is already in use!" % self.email)

        if self.save(verbose=False):
            self.logger.warn('Created new user! %s' % self)
        else:
            raise AttributeError('New user record could not be saved!')

        self.update_password(self.kwargs.get('password'))


    def update_password(self, new_password=None):
        """ Hashes 'new_password' and saves it as the password. """

        self.password = generate_password_hash(new_password)

        if self.save(verbose=False):
            self.logger.warn('Updated password! %s' % self)
        else:
            raise AttributeError('Password update failed!')


    def check_password(self, password=None):
        """ Checks 'password' kwarg against the db. """
        return check_password_hash(self.password, password)


    #
    #   gets and sets
    #

    def get_avatar(self, size):
        """ Some additional, user-specific loads. """

        digest = md5(self.email.encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size
        )
