'''
CGM-Manager
'''
# TODO: Improve logging (more verbose, uptime, start & exit...)
# TODO: hashing files and log it.

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import logging
import time
import datetime
import re

if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser

import cgmlog
import cgmclass

class Uptime(object):
    """Class for logging uptime once per defined amount of seconds"""
    def __init__(self, seconds):
        self.start = datetime.datetime.now()
        self.last = self.start
        self.delta = datetime.timedelta(0, seconds)
    def log(self):
        now = datetime.datetime.now()
        d = now - self.last
        if d >= self.delta:
            logging.info('Running for %s', now - self.start)
            self.last = now

SRC_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
uptime = Uptime(3600)

def ExtFilter(path, extfilter):
    ext = os.path.splitext(path)[1]
    return re.match(extfilter, ext, re.I) is not None

def TranslateDir(dirname):
    try:
        cgmlist = [ os.path.join(dirname, fname)
            for fname in os.listdir(dirname)
            if ExtFilter(fname, '.cgm') ]
    except OSError as err:
        logging.error('Cannot list dir "%s": %s', dirname, err.strerror)
        return

    for fname in cgmlist:
        try:
            cgm = cgmclass.CGMfile(fname)
        except ValueError:
            pass
        else:
            cgm.TranslateAll()


def main():
    conf = configparser.RawConfigParser()

    try:
        conf.read(os.path.join(SRC_DIR, 'cgmman.ini'))
        cgmdir = conf.get('CGMMAN', 'cgmdir')
        workdir = conf.get('CGMMAN', 'workdir')
        sleeptime = conf.getint('CGMMAN', 'sleeptime')
        loglevel = conf.get('CGMMAN', 'loglevel')
    except configparser.Error as err:
        print("Error in configuration file", file=sys.stderr)
        print(err, file=sys.stderr)
        sys.exit(1)

    # TODO: create workdir if it doesn't exist
    os.chdir(workdir)
    cgmlog.basicConfig('cgmman', loglevel)

    try:
        logging.info('Starting CGM-Manager')
        translators = os.path.join(SRC_DIR, 'Translators.ini')
        cgmclass.addTranslatorsFromFile(translators)
        while not os.path.isfile('stop'):
            uptime.log()
            TranslateDir(cgmdir)
            time.sleep(sleeptime)
        logging.info('Stopping CGM-Manager')
        os.remove('stop')
    except:
        logging.exception('Unexpected exception')
        raise

if __name__ == '__main__':
    main()
