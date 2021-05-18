import configparser
import os
import time
import argparse

def findLostFiles(dirs, id):
  lostfiles = []
  for dir in dirs:
    files = os.listdir(dir)
    for fname in files:
      if id in fname:
        lost = os.path.join(dir, fname)
        if lost not in lostfiles:
          lostfiles.append(lost)
  return lostfiles

parser = argparse.ArgumentParser(description='Delete lost plotting files')
parser.add_argument('--delete', action='store_true', help='delete the lost plot files')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.conf')
configTimeout = int(config['MAIN']['timeout'])
logfiledir = config['MAIN']['logdir']

logfiles = os.listdir(logfiledir)
now = time.time()

print('checking {0} logfiles in {1}'.format(len(logfiles), logfiledir))

for lf in logfiles:
  fullpath = os.path.join(logfiledir, lf)
  if os.path.isfile(fullpath):
    moddelta = now - os.path.getmtime(fullpath)

    # check stall files
    if moddelta > configTimeout:
      with open(fullpath, 'r') as f:
        content = f.read()
        if 'Copied final file' not in content:
          contentLines = content.splitlines()
          id = contentLines[5].split()[1]
          dirs = contentLines[4].partition('Starting plotting progress into temporary dirs: ')[2]
          dir1 = dirs.partition(' and ')[0]
          dir2 = dirs.partition(' and ')[2]

          lostfiles = findLostFiles([dir1, dir2], id)
          if len(lostfiles) > 0:
            print('{0} is dead since {1} minutes - {2} files remaining'.format(lf, int(moddelta/60), len(lostfiles)))
            if args.delete:
              print(' ... deleting files')
              for delfile in lostfiles:
                os.remove(delfile)
