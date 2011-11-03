"""
CGMfile Object definition
"""

import os
import re
import shutil

def _remove(path):
   # os.remove() wrapper
   try:
      os.remove(path)
   except:
      logging.exception("Cannot remove %s", path)

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
         raise ValueError(path)
      self.name = re.sub('^trasp_', '', self.name, flags=re.I)

      # Replace variables in command list
      for k in self._translator.keys():
         (retOk, commandlist) = self._translator[k]
         self.addTranslator(k, retOk, commandlist)

   def __del__(self):
      for f in self._files: _remove(f)

   def __str__(self):
      return self.path

   def _Get(self):
      # Copy CGM file to working dir
      if self.filename not in self._files:
         try:
            shutil.copyfile(self.path, self.filename)
         except OSError:
            logging.exception('Cannot copy "%s" in "%s"', self.path,
               os.getcwd())
            raise
         self._files.append(self.filename)

   def _Put(self, ext):
      # Copy file name.ext in CGM original dir
      f = os.name + ext
      if f not in self._files:
         logging.critical('CGMfile._Put(): File "%s" was not created', f)
      try:
         shutil.copyfile(f, os.path.join(self.dirname, f))
      except OSError:
         logging.exception('Cannot copy "%s" in "%s"', f, self.dirname)

   def addTranslator(self, ext, retOk, commandlist):
      """
      Add a translator definition for current object.

      Arguments are like cgmclass.addTranslator() args.
      """
      command = [s.format(cgmfile=self.basename, name=self.name)
                  for s in commandlist]
      self._translator[ext] = (retOk, commandlist)

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
   CGMfile._translator[ext] = (retOk, commandlist)
