"""

    The image object lives here (at the bottom).

    Up top, helper/laziness methods for working with images.

"""

# standard library
from datetime import datetime
import os

# second party
from bson.objectid import ObjectId
import PIL.Image
from werkzeug.utils import secure_filename

# application imports
from app import app, models, util


#
#   helper and laziness methods
#

def expand_image(oid=None):
    """ Pass in an image OID to get the MDB record for that image back as a
    dict. """

    if not ObjectId.is_valid(oid):
        raise ValueError("Invalid image asset OID! %s" % oid)

    record = app.config['MDB'].images.find_one({'_id': oid})
    if record is None:
        err = "OID '%s' not associated with an image!" % oid
        app.logger.error(err)
        app.logger.error('Using default image...')
        record = {'base_name': 'unknown_image.jpg'}

    return dict(record)


#
#   The Image object
#

class Image(models.Model):
    """ Images! """

    def __init__(self, *args, **kwargs):

        models.Model.__init__(self,  *args, **kwargs)
        self.collection = 'images'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            'base_name': str,
            'created_on': datetime,
            'created_by': ObjectId,
            'updated_on': datetime,
            'long_edge': str,
        }

        self.load()


    def __repr__(self):
        return '<Image {}>'.format(self.base_name)


    def new(self):
        """ Writes an image to the FS; indexes it in the DB. """

        if 'raw_upload' not in self.kwargs:
            err = "The '%s' kwarg is required when creating a new user!"
            raise ValueError(err % 'raw_upload')

        in_file = self.kwargs.get('raw_upload')

        # set the basename
        self.base_name = (
            datetime.now().strftime(util.YMD) + "_" +
            secure_filename(in_file.filename)
        )

        # first handle the upload
        if not os.path.isdir(app.config['UPLOADS']):
            self.logger.warn(
                'Creating uploads folder! %s' % app.config['UPLOADS']
            )
            os.mkdir(app.config['UPLOADS'])

        # set the target (base) name
        target_name = os.path.splitext(self.base_name)[0] + '.webp'

        # write the file to tmp, then convert it
        in_file.save(os.path.join("/tmp/", self.base_name))
        im = PIL.Image.open(os.path.join('/tmp', self.base_name))
        im.save(
            os.path.join(app.config['UPLOADS'], target_name),
            'webp',
            quality=100
        )

        # set the long edge
        self.long_edge = 'vertical'
        if im.height < im.width:
            self.long_edge = 'horizontal'

        self.base_name = target_name

        # double check it!
        abs_path = os.path.join(app.config['UPLOADS'], self.base_name)
        if not os.path.isfile(abs_path):
            self.logger.error('Image file does not exist! %s' % abs_path)
            raise OSError('Could not create image! %s' % abs_path)

        # now write the db record
        self.created_on = datetime.now()

        # check for pre-existing to determine what to do
        record = self.mdb.find_one({'base_name': self.base_name})
        if record is not None:
            action = 'Updated'
            self.updated_on = datetime.now()
            self._id = record['_id']
        else:
            action = 'Created'
            self.created_on = datetime.now()
            self._id = self.mdb.insert({'base_name': self.base_name})

        if self.save(verbose=False):
            self.logger.warn('%s image! %s' % (action, self))
        else:
            raise AttributeError('New image record could not be saved!')


    def delete(self):
        """ Removes the record and the file. """

        os.remove(self.get_abs_path())
        self.logger.warn('Removed file! %s' % self.get_abs_path())
        super().delete()
        return True


    #
    #   GET methods
    #

    def get_abs_path(self):
        """ Gets the absolute path to the file. """
        return os.path.join(app.config['UPLOADS'], self.base_name)

