"""
Logging module for CGM-Manager.
"""

import logging
import logging.handlers
import time
import os.path

# There is no logging handler with needed features, so we write one
class DailyRotatingFileHandler(logging.handlers.BaseRotatingHandler):
    """
    Handler for daily rotating log files. After midnight it writes log entries
    into a new log file so you get a logfile a day.
    """
    # Interesting inherited attributes:
    # self.stream: File like Object
    # self.baseFilename = os.path.abspath(logfile)
    # self.mode: Mode used to open log file

    def __init__(self, fileprefix, encoding=None):
        """
        Open the file prefix.date.log and use it as destination for logging.

        Rollover occurs when file date mismatch with current date.
        """
        self.__date =  time.strftime("%Y-%m-%d")
        self.__prefix = fileprefix
        filename = "{0}.{1}.log".format(self.__prefix, self.__date)
        logging.handlers.BaseRotatingHandler.__init__(self, filename, 'a', encoding)

    def shouldRollover(self, record):
        'Check if date changed since last write'
        return time.strftime("%Y-%m-%d") != self.__date

    def doRollover(self):
        'Close log file and open a new one based on date'
        self.__date = time.strftime('%Y-%m-%d')
        self.stream.close()
        self.stream = None
        # Set new baseFilename but do not open stream,
        # we expect parent classes do it when needed
        dirname = os.path.dirname(self.baseFilename)
        filename = '{0}.{1}.log'.format(self.__prefix, self.__date)
        self.baseFilename = os.path.join(dirname, filename)
        # TODO: We can gzip old log file

def basicConfig(fileprefix, level=logging.INFO):
    """
    Wrapper to logging.basicConfig()

    Add a DailyRotatingFileHandler to the root logger using fileprefix as
    a prefix for filename. Filename is calculated as <prefix>.<date>.log
    and is created a log file a day.
    """
    fmt = logging.Formatter('%(asctime)s - %(levelname)-10s - %(message)s',
                            '%H:%M:%S')

    hl = DailyRotatingFileHandler(fileprefix)
    hl.setLevel(level)
    hl.setFormatter(fmt)

    logger = logging.getLogger('')
    logger.setLevel(level)
    logger.addHandler(hl)
