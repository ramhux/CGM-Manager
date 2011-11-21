'''
CGM-Manager
'''

import os
import sys
import ConfigParser
import logging
import time
import re

import cgmlog
import cgmclass

srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))

def ExtFilter(path, extfilter):
    ext = os.path.splitext(path)[1]
    return re.match(extfilter, ext, re.I) is not None

def TranslateDir(dirname):
    cgmlist = [ os.path.join(dirname, fname)
        for fname in os.listdir(dirname)
        if ExtFilter(fname, '.cgm') ]
    for fname in cgmlist:
        try:
            cgm = cgmclass.CGMfile(fname)
        except ValueError:
            pass
        else:
            cgm.TranslateAll()

def main():
    conf = ConfigParser.RawConfigParser()
    with open(os.path.join(srcdir, 'cgmman.ini')) as f:
        conf.readfp(f)
    cgmdir = conf.get('CGMMAN', 'cgmdir')
    workdir = conf.get('CGMMAN', 'workdir')
    sleeptime = conf.getint('CGMMAN', 'sleeptime')
    loglevel = conf.get('CGMMAN', 'loglevel')

    os.chdir(workdir)
    cgmlog.basicConfig('cgmman', loglevel)
    cgmclass.addTranslatorsFromFile(os.path.join(srcdir, 'Translators.ini'))

    # TODO: create global try..except and log exceptions 
    while not os.path.isfile('stop'):
        TranslateDir(cgmdir)
        time.sleep(sleeptime)
    os.remove('stop')

if __name__ == '__main__':
    main()
