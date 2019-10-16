"""

    This script is used to initialize the app. DO NOT customize.

"""

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])
#    app.run(host='127.0.0.1', port=app.config['PORT'], ssl_context='adhoc')    # prod testing
