# ngram v2020 Annual-Parser
# Just Python

import gensim
import logging
import os
import sys
import itertools
from smart_open import smart_open
import time


# logging
logging.basicConfig(filename="just_py2.log", encoding="utf-8", level=logging.INFO)


class YearlyArrayUpdater(object):
  def __init__(self, yearly_dirname: str, update_limit: int):
    # year-[line;] dictionary
    self.yearly_lines = [];
    self.yearly_dirname = yearly_dirname
    self.update_limit = update_limit
    self.time = time.time()
  
  def insert(self, yearly_line):
    self.yearly_lines.append(yearly_line)

    if len(self.yearly_lines)>=self.update_limit:
      self._update()

  def finish(self):
    if len(self.yearly_lines)>0:
      self._update()

  def _update(self):
    collect_yearly_lines = dict()
    for (year, line) in self.yearly_lines:
      if collect_yearly_lines.get(year):
        collect_yearly_lines[year].append(line)
      else:
        collect_yearly_lines[year] = [line]

    for year, array in collect_yearly_lines.items():
      yearly_file = os.path.join(self.yearly_dirname, str(year))
    
      with smart_open(yearly_file, 'a', encoding="utf8") as fin:
        fin.writelines(array)
    
    # clear rest
    self.yearly_lines.clear()

    # logging time for bechmark test
    t = time.time()-self.time
    logging.info(t)



# Processing ngram files(ver.2020) in 'dirname'
# Save processed-annual-files inside 'yearly_dirname'
# The yearly-making-process would start from the initiation!
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

          line_split = line.split("\t")
          if len(line_split)<2:
            continue
          ngram = line_split[0]

          # case of not using tag
          if "_" in ngram:
            continue

          year_counts = line_split[1:]
          
          for ycc in year_counts:
            ycc=ycc.split(",")
            if len(ycc)==3:
              try:
                year, match_count = int(ycc[0]), ycc[1]
                ngram_count = "/t".join([ngram, match_count]) # in the format of "(ngram) \t (match_count)"
                ngram_count += "/n"

                yearly_array_updater.insert((year, ngram_count))
              except:
                # print(f"Error in parsing each line. The line is <{line}>")
                continue

      #t = time.time()-t0
      #print(f"processing file {fname} took {round(t, 2)}sec.")

    # finish yearly_array_updater
    yearly_array_updater.finish()

    #t_end = time.time()
    #print(f"make_yearly_time finishes. {round((t_end-t_start)/60, 2)}min took.")

    return True



# command line example:
if __name__ == '__main__':
  args = sys.argv
  if len(args) != 3:
    raise ValueError("#")
  
  dirname = args[1]
  yearly_dirname = args[2]

  maker = YearlyMaker(dirname, yearly_dirname, update_limit=10_000_000)