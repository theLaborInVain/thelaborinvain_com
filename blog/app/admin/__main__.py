"""

    Administration operations!

"""

import getpass
from optparse import OptionParser
import sys

# project imports
from app import admin

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
    parser.add_option("--add_user", dest="add_user", default=False,
        help="Create a new user", action='store_true',)
    parser.add_option("--list_users", dest="list_users", default=False,
        help="Dump a list of users", action='store_true',)
    parser.add_option("--set_password", dest="set_password", default=False,
        help="Interactively set a user's password", action='store_true',)
    parser.add_option("--initialize", action="store_true", dest="initialize",
        default=False, help="Burn it down. Start over.")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose",
        default=True, help="don't print status messages to stdout")

    (options, args) = parser.parse_args()

    admin_object = admin.AdministrationObject()

    if options.initialize:
        print('')
        admin_object.initialize()
        print('\n - Project Initialized!\n  exiting...\n')
        sys.exit(0)

    if options.add_user:
        admin_object.add_user(*create_user())

    if options.list_users:
        for user in admin_object.dump_users():
            print(user)

    if options.set_password:
        admin_object.set_password(*set_password())



