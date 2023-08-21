# ngram v2020 Yearly-Parser

import gensim
import os
import shutil
import sys
import itertools
from smart_open import smart_open
import time

# logging
import logging
logging.basicConfig(filename="yearly_parser.log", encoding="utf-8", level=logging.INFO)


# import rustlib
# Below copyfile codes are for under MS WINDOWS circumstances.
# Under Linux, use .so file instead of .dll file.
rustlib_src = "../rustlib/target/release/rustlib.dll"
rustlib_dst = "./rustlib.pyd"
shutil.copyfile(rustlib_src, rustlib_dst)

import rustlib


# This class collects newly parsed lines and make yearly file regularly.
# Arguments:
#   yearly_dirname (str): directory path to store new yearly files.
#   update_limit (int): parsed lines store limit to make a new yearly file.
class YearlyArrayUpdater(object):
  def __init__(self, yearly_dirname: str, update_limit: int):
    self.yearly_lines = []
    self.yearly_dirname = yearly_dirname
    self.update_limit = update_limit
    self.time = time.time()
  
  def insert_lines(self, yearly_lines):
    self.yearly_lines.extend(yearly_lines)

    if len(self.yearly_lines)>=self.update_limit:
      self._update()

  def finish(self):
    if len(self.yearly_lines)>0:
      self._update()

  def _update(self):
    collect_yearly_lines = rustlib.collect_lines(self.yearly_lines)
    for year, array in collect_yearly_lines.items():
      yearly_file = os.path.join(self.yearly_dirname, str(year))

      with smart_open(yearly_file, 'a', encoding="utf8") as fin:
        fin.writelines(array)
    
    # clear rest
    self.yearly_lines.clear()

    # logging time for bechmark test
    t = time.time()-self.time
    logging.info(t)
    #print("updated", t)


# This class parses each ngram(v.2020) lines into new yearly formated lines.
# Collect new lines in the object of YearlyArrayUpdater so as to make new files.
#   dirname (str): directory path to retrieve raw file of ngram(v.2020).
#   yearly_dirname (str): directory path to store new yearly files.
#   update_limit (int): parsed lines store limit to make a new yearly file.
class YearlyMaker(object):
  def __init__(self, dirname, yearly_dirname, limit=None, update_limit=10_000_000):
    self.dirname = dirname
    self.yearly_dirname = yearly_dirname
    self.limit = limit
    self.update_limit=update_limit
    # start the process from the initiation.
    self._make_yearly_file()

  def _make_yearly_file(self):
    
    #t_start = time.time()
    #print("make_yearly_file starts.")

    yearly_array_updater = YearlyArrayUpdater(self.yearly_dirname, self.update_limit)

    for fname in os.listdir(self.dirname):
      #t0 = time.time()

      with smart_open(os.path.join(self.dirname, fname)) as fin:
        for line in itertools.islice(fin, self.limit):
          line = gensim.utils.to_unicode(line)

          yearly_lines = rustlib.parse_line(line)
          yearly_array_updater.insert_lines(yearly_lines)

      #t = time.time()-t0
      #print(f"processing file {fname} took {round(t, 2)}sec.")

    # finish yearly_array_updater
    yearly_array_updater.finish()

    #t_end = time.time()
    #print(f"make_yearly_time finishes. {round((t_end-t_start)/60, 2)}min took.")

    return True
  

# command line example:
# ```
# python yearly_parser.py "../dir-of-ngram", "./dir-of-new-yearly-files"
# ```
if __name__ == '__main__':
  args = sys.argv
  if len(args) != 3:
    raise ValueError("#")
  
  dirname = args[1]
  yearly_dirname = args[2]

  maker = YearlyMaker(dirname, yearly_dirname, update_limit=10_000_000)



