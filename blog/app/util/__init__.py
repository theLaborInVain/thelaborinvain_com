"""

    Utilities, such as logging, live here.


"""

# standard lib
import logging
import os
import string
import sys

# second party
from bs4 import BeautifulSoup

# app imports
from app import app


# CONSTANTS
YMD = "%Y-%m-%d"
YMDHMS = "%Y-%m-%d %H:%M:%S"


def get_logger(log_level=None, log_name=None):
    """ Initialize a logger. Defaults come from config.py. """

    # defaults
    log_root_dir = os.path.join(app.root_path, '..', 'logs')
    if log_level is None:
        if app.config['DEBUG']:
            log_level = 'DEBUG'
        else:
            log_level = 'INFO'
    if log_name is None:
        log_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if log_name == '':
        log_name = 'default'

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    if len(logger.handlers):    # if we're initializing a log, kill other
        logger.handlers = []    # open handles, so the latest init wins

    if not len(logger.handlers):    # if it's not already open, open it

        # now check the logging root, create it if it's not there
        if not os.path.isdir(log_root_dir):
            os.mkdir(log_root_dir)

        # create the path and add it to the handler
        log_path = os.path.join(log_root_dir, log_name + ".log")
        logger_fh = logging.FileHandler(log_path)

        #   set the formatter and add it via addHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s:\t%(message)s', YMDHMS
        )
        logger_fh.setFormatter(formatter)
        logger.addHandler(logger_fh)

    return logger



def string_to_handle(s):
    """ Turns a string into a handle, suitable for use as a URL. """

    s = s.lower()
    trans_table = str.maketrans('', '', string.punctuation)
    s = s.translate(trans_table)
    s = s.replace(" ", "_")

    return s


def fancy_html(s, apply_p_blocks=True):
    """ Accepts a string; returns fancy-ass HTML with all of our cool stuff."""

    s = str(s)
    if apply_p_blocks:
        raw = "".join(["<p>%s</p>" % p for p in s.split('\n') if p != ''])
    else:
        raw = str(s)

    # expand links -- do this before we get to HTML junk
    raw_list = raw.split(" ")
    for word in raw_list:
        if word[:8] == 'https://':
            index = raw_list.index(word)
            url = word
            if url[-1] in [',','.']:
                url = url[:-1]
            raw_list[index] = '<a href="%s">%s</a>' % (url,word)
    raw = " ".join(raw_list)

    soup = BeautifulSoup(raw, 'html.parser')

    # fix anchors
    for anchor in soup.find_all('a'):
        if 'fancy' not in anchor.get('class', []):
            anchor['class'] = anchor.get('class', []) + ['fancy']

        anchor['target'] = 'top'

    return str(soup)
