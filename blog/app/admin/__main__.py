"""

    Administration operations!

"""

import getpass
from optparse import OptionParser
import sys

# second party imports
#from bson.objectid import ObjectId

# project imports
from app import admin, models
from app.models import posts

def create_user():
    """ Gets new user stuff from CLI prompts. High tech shit! """

    print('')
    name = input("  Name? ")
    email = input("  Email? ")
    password = getpass.getpass(prompt='  Password: ', stream=None)

    return name.strip(), email.lower().strip(), password

def set_password():
    """ Gets new user stuff from CLI prompts. High tech shit! """

    print('')
    email = input("  Email? ")
    password = getpass.getpass(prompt='  Password: ', stream=None)

    return email.lower().strip(), password


if __name__ == "__main__":

    parser = OptionParser()

    # users
    parser.add_option("--add_user", dest="add_user", default=False,
        help="Create a new user", action='store_true',)
    parser.add_option("--list_users", dest="list_users", default=False,
        help="Dump a list of users", action='store_true',)
    parser.add_option("--set_password", dest="set_password", default=False,
        help="Interactively set a user's password", action='store_true',)

    # posts
    parser.add_option("-p", dest="post_oid", default=None,
        help="Work with a post.")

    # tags
    parser.add_option("--list_tags", dest="list_tags", default=False,
        help="Dump a list of tags", action='store_true',)
    parser.add_option("-t", dest="tag_oid", default=None,
        help="Work with a tag.")
    parser.add_option("--set_tag_name", dest="set_tag_name", default=None,
        help="Updates a tag's name. REQUIRES -t", type=str)

    # DANGER ZONE
    parser.add_option("--initialize", action="store_true", dest="initialize",
        default=False, help="Burn it down. Start over.")

    (options, args) = parser.parse_args()

    admin_object = admin.AdministrationObject()

    # INITIALIZE!!!!
    if options.initialize:
        print('')
        admin_object.initialize()
        print('\n - Project Initialized!\n  exiting...\n')
        sys.exit(0)

    # user admin first
    if options.add_user:
        admin_object.add_user(*create_user())
    if options.list_users:
        for user in admin_object.get_collection('users'):
            print(user)
    if options.set_password:
        admin_object.set_password(*set_password())

    # post admin
    if options.post_oid is not None:
        post_object = posts.Post(_id=options.post_oid)
        print(post_object)

    # tag admin
    if options.list_tags:
        for tag in admin_object.get_collection('tags'):
            print(tag)

    if options.tag_oid is not None and options.set_tag_name is not None:
        new_name = options.set_tag_name.strip()
        print(" Setting tag name to '%s' (%s)" % (new_name, type(new_name)))
        updated_record = admin_object.set_attribute(
            collection = 'tags',
            asset_oid = options.tag_oid,
            attrib = 'name',
            value = new_name
        )
        print(" " + str(updated_record))


