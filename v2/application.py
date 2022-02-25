'''

    This application.py is meant to be used in AWS EB deployment!

    If it looks sparse, that's because it is and we don't want to break EB.

'''

from app import application

if __name__ == "__main__":
    application.run()
