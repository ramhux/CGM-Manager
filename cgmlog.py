"""
Logging module for CGM-Manager.
"""
from __future__ import print_function
from __future__ import unicode_literals

import logging.handlers
import time
import os.path


# There is no logging handler with needed features, so we write one
class DailyRotatingFileHandler(logging.handlers.BaseRotatingHandler):
    
    """
    Handler for daily rotating log files.
    
    After midnight it writes log entries into a new log file so you get
    a logfile a day.
    """

    # Interesting inherited attributes:
    # self.stream: File like Object
    # self.baseFilename = os.path.abspath(logfile)
    # self.mode: Mode used to open log file

    def __init__(self, fileprefix, encoding=None):
        """
        Open a log file.
        
        The file prefix.date.log is opened for logging, and rollover occurs
        when file date mismatch with current date.
        """
        self.__date =  time.strftime("%Y-%m-%d")
        self.__prefix = fileprefix
        filename = "{0}.{1}.log".format(self.__prefix, self.__date)
        logging.handlers.BaseRotatingHandler.__init__(self, filename, 'a',
                                                      encoding)

    def shouldRollover(self, record):
        """Check if date changed since last write."""
        return time.strftime("%Y-%m-%d") != self.__date

    def doRollover(self):
        """Close log file and open a new one based on date."""
        self.__date = time.strftime('%Y-%m-%d')
        if self.stream:
            self.stream.close()
        self.stream = None
        # Set new baseFilename but do not open stream,
        # we expect parent classes do it when needed
        dirname = os.path.dirname(self.baseFilename)
        filename = '{0}.{1}.log'.format(self.__prefix, self.__date)
        self.baseFilename = os.path.join(dirname, filename)
        # TODO: We can gzip old log file


def basicConfig(fileprefix, level='INFO'):

    """
    Wrapper to logging.basicConfig()

    Set a default format, add a DailyRotatingFileHandler to the root
    logger and set log level as defined by kword level. A log file a
    day is created as <prefix>.<date>.log.
    
    Valid log levels are DEBUG, INFO, WARNING, ERROR and CRITICAL.
    Numerical levels are accepted.
    """

    if not isinstance(level, int):
        level = getattr(logging, level)

    fmt = logging.Formatter('%(asctime)s - %(levelname)-10s - %(message)s',
                            '%H:%M:%S')

    hl = DailyRotatingFileHandler(fileprefix)
    hl.setLevel(level)
    hl.setFormatter(fmt)

    logger = logging.getLogger('')
    logger.setLevel(level)
    logger.addHandler(hl)
