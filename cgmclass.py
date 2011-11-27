"""
CGMfile Object definition
"""
from __future__ import print_function

import os
import re
import shutil
import logging
import subprocess
import shlex
import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser

def _remove(path):
    # os.remove() wrapper
    try:
        os.remove(path)
    except OSError as err:
        logging.error('Cannot remove "%s": %s', err.filename, err.strerror)

class CGMfile:
    """
    This class implements a CGM file identified by path and a set of methods
    for converting to other formats. Format conversion is performed by
    translators (external programs) as defined by developer.

    Translators may be defined per object, or globally. If globally defined,
    translators are inherited by new CGMfile objects.

    Filenames follow this rules:
    - Case is ignored when looking for existing files (running on Windows)
    - 'filename.ext' and 'trasp_filename.ext' are equivalent
    - It is expected that the names of newly created files is 'filename.ext',
       so be careful with translator definitions
    """
    _translator = {}

    def __init__(self, path):
        """
        cgmclass.CGMfile(path) -> CGMfile Object

        Argument is a path to a file with '.cgm' extension.
        """
        self._translator = self._translator.copy() # avoid modify class attr.
        self._files = [] # list of temp files in working dir

        self.path = os.path.abspath(path)
        self.dirname, self.filename = os.path.split(self.path)
        self.name, ext = os.path.splitext(self.filename)
        if not re.match('.cgm', ext, re.I) or not os.path.isfile(self.path):
            logging.warning('%s: Invalid CGM file', self.path)
            raise ValueError(path)
        self.name = re.sub('^trasp_', '', self.name, flags=re.I)

        # Replace variables in command list
        for k in self._translator.keys():
            (retOk, commandlist) = self._translator[k]
            self.addTranslator(k, retOk, commandlist)

    def __del__(self):
        for f in self._files:
            _remove(f)

    def __str__(self):
        return self.path

    def _Get(self):
        # Copy CGM file to working dir
        if self.filename not in self._files:
            try:
                shutil.copyfile(self.path, self.filename)
            except EnvironmentError as err:
                logging.error('Cannot copy "%s" in "%s"', self.path,
                              os.getcwd())
                logging.error('    %s', err)
                raise
            else:
                self._files.append(self.filename)

    def _Put(self, ext):
        # Copy file name.ext in CGM original dir
        f = self.name + ext
        assert f in self._files, '{0} not in self._files'.format(f)
        try:
            shutil.copyfile(f, os.path.join(self.dirname, f))
        except EnvironmentError as err:
            logging.error('Cannot copy "%s" in "%s"', f, self.dirname)
            logging.error('    %s', err)
            raise

    def _shouldTranslate(self, ext):
        # Check if exists filename.ext in CGM dir
        filename = self.name + ext
        filetrasp = 'TRASP_' + filename
        filename = os.path.join(self.dirname, filename)
        filetrasp = os.path.join(self.dirname, filetrasp)
        return not (os.path.isfile(filename) or os.path.isfile(filetrasp))

    def Translate(self, ext):
        """
        Translate the CGM file using the proper translator, if it does not
        exist a translated version file.

        Temporal files are created in working directory
        
        Raised exceptions:
        - ValueError if ext is not a valid translator
        - OSError, shutil.Error if error copying files
        - OSError when calling external translator
        """
        if ext not in self._translator.keys():
            logging.critical('CGMfile.Translate(): No translator for "%s"', ext)
            raise ValueError(ext)
        if not self._shouldTranslate(ext):
            return

        newfile = self.name + ext
        logging.info('Translating: "%s" -> "%s"', self.filename, newfile)
        self._Get()
        (retOk, command) = self._translator[ext]
        if retOk == subprocess.call(command):
            self._files.append(newfile)
            self._Put(ext)
        else:
            logging.error('%s: Translator returned an error', newfile)

    def TranslateAll(self):
        """
        Translate the CGM file using every translator defined

        Exceptions are logged, but not raised
        """
        for ext in self._translator.keys():
            try:
                self.Translate(ext)
            except EnvironmentError:
                logging.error('Cannot translate: "%s" -> "%s"', self, ext)

    def addTranslator(self, ext, retOk, commandlist):
        """
        Add a translator definition for current object.

        Arguments are like cgmclass.addTranslator() args.
        """
        command = [s.format(cgmfile=self.filename, name=self.name)
                   for s in commandlist]
        self._translator[ext] = (retOk, command)

def addTranslator(ext, retOk, commandlist):
    """
    Add a translator definition for new CGMfile objects.

    Arguments description:
    - ext: file extension like '.tif'
    - retOk: return code for Ok translation (usually 0)
    - commandlist: list of arguments used to run the external program.
      for example ['C:\\\\cgm2tif.exe', 'file.cgm', 'file.tif']

    The following special strings can be used:
    '{cgmfile}' is replaced by CGM file name
    '{name}' is replaced by CGM file name without extension
    """
    logging.info('Setting "%s" translator', ext)
    CGMfile._translator[ext] = (retOk, commandlist)

def addTranslatorsFromFile(filename):
    """
    Add a set of translators definitions as defined inside file.

    File has INI-like format, with file extensions as sections and 3 key=value
    pairs: translator, args, and success.
    - Translator is a Win32 app path
    - Args is a list of arguments passed to translator, separated by
      whitespaces. You can use quotes if needed.
    - Success is the exit status when all went well

    [.ext]
    translator = C:\\Program Files\\cgm2ext.exe
    args = {cgmfile} {name}.ext
    success = 0
    """
    logging.info('Reading translators from "%s"', filename)
    config = configparser.RawConfigParser()
    with open(filename) as cfgfile:
        config.readfp(cfgfile)

    for ext in config.sections():
        retOk = config.getint(ext, 'success')
        args = config.get(ext, 'args')
        command = shlex.split(args)
        command.insert(0, config.get(ext, 'translator'))
        addTranslator(ext, retOk, command)
