"""

    The figure object lives here.


"""

# standard library
from copy import copy
from datetime import datetime
import os

# second party
from bson.objectid import ObjectId

# application imports
from app import app, models, util
from app.models import images


#
#   The Figure object
#

class Figure(models.Model):
    """ Figures are SORT OF like posts, except that they're meant to be used,
    primarily, to supplement post information. They're sort of like a tag, but
    contain a lot more data. """

    def __init__(self, *args, **kwargs):

        models.Model.__init__(self,  *args, **kwargs)
        self.collection = 'figures'
        self.mdb = app.config['MDB'][self.collection]

        self.data_model = {
            'created_on': datetime,
            'created_by': ObjectId,
            'updated_on': datetime,
            'name': str,
            'game': str,
            'publisher': str,
            'concept_art': list,        # OIDs of Image records
            'concept_art_by': str,
            'unpainted': list,          # OIDs of Image records
            'sculpted_by': str,
            'longest_dimension': int,
            'tags': list,
        }

        self.required_attribs = [
            'name',
            'publisher',
        ]

        self.load()


    def __repr__(self):
        return '<Figure {}>'.format(self.name)


    def save(self, verbose=True):
        """ Forces OID lists to be OID lists. """

        for image_list in ['concept_art', 'unpainted', 'tags']:
            corrected_list = []
            for image_oid in getattr(self, image_list, []):
                corrected_list.append(ObjectId(image_oid))
            setattr(self, image_list, corrected_list)

        return super().save(verbose)


    def serialize(self):
        """ Returns a fancy version of a figure, with expanded image lists. """

        output = copy(self.record)

        for image_list in ['concept_art', 'unpainted']:
            expanded_list = []
            for image_oid in output.get(image_list, []):
                expanded_list.append(images.expand_image(image_oid))
            output[image_list] = expanded_list

        return output

