'''
CGM-Manager
'''
# TODO: Improve logging (more verbose, uptime, start & exit...)

import os
import sys
import ConfigParser
import logging
import time
import re

import cgmlog
import cgmclass

SRC_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

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
    conf = ConfigParser.RawConfigParser()

    try:
        conf.read(os.path.join(SRC_DIR, 'cgmman.ini'))
        cgmdir = conf.get('CGMMAN', 'cgmdir')
        workdir = conf.get('CGMMAN', 'workdir')
        sleeptime = conf.getint('CGMMAN', 'sleeptime')
        loglevel = conf.get('CGMMAN', 'loglevel')
    except ConfigParser.Error as err:
        print >>sys.stderr, "Error in configuration file"
        print >>sys.stderr, err
        sys.exit(1)

    os.chdir(workdir)
    cgmlog.basicConfig('cgmman', loglevel)

    try:
        logging.info('Starting CGM-Manager')
        translators = os.path.join(SRC_DIR, 'Translators.ini')
        cgmclass.addTranslatorsFromFile(translators)
        while not os.path.isfile('stop'):
            TranslateDir(cgmdir)
            time.sleep(sleeptime)
        logging.info('Stopping CGM-Manager')
        os.remove('stop')
    except:
        logging.exception('Unexpected exception')
        raise

if __name__ == '__main__':
    main()
