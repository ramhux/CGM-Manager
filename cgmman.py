'''
CGM-Manager
'''

import os
import sys
import ConfigParser
import logging
import time

import cgmlog
import cgmclass

srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))

def ExtFilter(path, extfilter):
    name, ext = os.path.splitext(path)
    return re.match(extfilter, ext, re.I) is not None

def TranslateDir(dirname):
    cgmlist = [ os.path.join(dirname, f)
        for f in os.listdir(dirname)
        if ExtFilter(f, '.cgm') ]
    for f in cgmlist:
        try:
            cgm = cgmclass.CGMfile(f)
        except ValueError:
            logging.warning('Invalid CGM file: %s', f)
        else:
            cgm.TranslateAll()

if __name__ == '__main__':
    conf = ConfigParser.RawConfigParser()
    with open(os.path.join(srcdir, 'cgmman.ini')) as f:
        conf.readfp(f)
    cgmdir = conf.get('CGMMAN', 'cgmdir')
    workdir = conf.get('CGMMAN', 'workdir')
    sleeptime = conf.getint('CGMMAN', 'sleeptime')
    loglevel = conf.get('CGMMAN', 'loglevel')
    loglevel = getattr(logging, loglevel)
    
    os.chdir(workdir)
    cgmlog.basicConfig('cgmman', loglevel)
    cgmclass.addTranslatorsFromFile(os.path.join(srcdir, 'Translators.ini'))
    
    while not os.path.isfile('stop'):
        TranslateDir(cgmdir)
        time.sleep(sleeptime)
