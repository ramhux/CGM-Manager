'''
CGM-Manager
'''

import os
import sys
import ConfigParser
import logging

srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))


if __name__ == '__main__':
    conf = ConfigParser.RawConfigParser()
    with open(os.path.join(srcdir, 'cgmman.ini')) as f:
        conf.readfp(f)
    cgmdir = conf.get('CGMMAN', 'cgmdir')
    workdir = conf.get('CGMMAN', 'workdir')
    sleeptime = conf.getint('CGMMAN', 'sleeptime')
    loglevel = conf.get('CGMMAN', 'loglevel')
    loglevel = getattr(logging, loglevel)