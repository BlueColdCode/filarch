#!/usr/bin/env python3

import sys, os
import datetime
import filecmp
from pathlib import PurePath, Path
from PIL import Image
import shutil
import string

options = {'recurse': False, 'merge': False, 'extension': '.jpg', 'debug': False}
filenum_on_date = {}


#input: date of the file creation.
#input: seqno: the sequence number of the file created at the same moment.
# return string filename based on date.
def filename_on_date(dt, seqno = 0):
    pref = '1' if dt.strftime('%Y') == '19' else '2'
    newfilename = pref + dt.strftime('%y') + ('%X' % dt.month) + dt.strftime('%d') +\
                  ('%c' % list(string.ascii_lowercase)[dt.hour]) + ('%.2d' % dt.minute) + ('%.2d' % (dt.second + seqno)) +\
                  options.extension
    return newfilename

# create the complete path of a file with the createdate, prefix.
def locate_dir(tofolder: Path, createdate: datetime) -> Path:
    cdate = createdate.strftime('%Y%m%d')
    tdate = None

    if options.debug:
        print("finding " + cdate + ' in', filenum_on_date.keys())

    for dt in sorted(filenum_on_date.keys()):
        if tdate == None: tdate = dt
        if dt <= cdate:
            tdate = dt
        else:
            break

    if tdate == None:
        raise Exception("Destination directory not found for " + cdate)

    return tofolder / createdate.strftime('%Y') / tdate

def move_files(fromfolder, tofolder):
    print(fromfolder, ' --> ', tofolder)

    for filename in sorted(os.listdir(fromfolder)):
        if not PurePath(filename).suffix.lower() == options.extension: continue
        try:
            oldfile = Path(fromfolder) / filename
            #print(fromfolder, oldfile)

            #figure out the destination directory
            ftags = Image.open(oldfile)._getexif()
            # some image files do not have EXIF tags.
            if ftags is None: continue
            createtimestamp = ftags[36867]
            createdate = datetime.datetime.strptime(createtimestamp, '%Y:%m:%d %H:%M:%S')
            destfolder = locate_dir(tofolder, createdate)

            # make up the new file name.
            newfile = destfolder / filename_on_date(createdate)

            # create the directory if it does not already exists.
            if not os.path.exists(destfolder):
                os.makedirs(destfolder)

            # keep finding new file name if a different file already exists
            seqno = 0
            while newfile.is_file():
                if not options.merge or not filecmp.cmp(oldfile, newfile, shallow=False):
                    seqno += 1
                    newfile = destfolder / filename_on_date(createdate, seqno)
                else:
                    break

            # move file.
            try:
                # try rename first.
                os.rename(oldfile, newfile)
            except:
                # try hard copy. throw exception if needed.
                shutil.copy2(oldfile, newfile)

            print(oldfile, ' > ', newfile)

        except Exception as e:
            print(e)
            continue

#input: fromdir with all the files.
#output: directory names and corresponding file number in each.
def tally_dirs(fromdir, tofolder):
    for folder, subfolders, files in os.walk(fromdir):
        for filename in os.listdir(folder):
            if not PurePath(filename).suffix.lower() == options.extension: continue
            try:
                oldfile = Path(folder) / filename

                # figure out the destination directory
                ftags = Image.open(oldfile)._getexif()
                # some image files do not have EXIF tags.
                if ftags is None: continue
                createtimestamp = ftags[36867]
                createdate = datetime.datetime.strptime(createtimestamp, '%Y:%m:%d %H:%M:%S')
                destname = createdate.date().strftime('%Y%m%d')

                if options.debug:
                    print(oldfile, "created on", createdate)

                destfolder = tofolder / createdate.strftime('$Y') / destname
                if os.path.exists(destfolder):
                    filenum_on_date[destname] = len(os.listdir(destfolder)) + 1
                elif filenum_on_date.get(destname) == None:
                    filenum_on_date[destname] = 1
                else:
                    filenum_on_date[destname] += 1
            except Exception as e:
                print(e)
                pass

    dates = sorted(filenum_on_date.keys())
    if options.debug:
        for dt in dates: print(dt, filenum_on_date[dt])

    collector_dt = None
    for dt in dates:
        # starting point to count
        if collector_dt == None or collector_dt[0:6] != dt[0:6]:
            collector_dt = dt
            continue

        # remove folder with insufficient files.
        if filenum_on_date[collector_dt] + filenum_on_date[dt] < 100:
            filenum_on_date[collector_dt] += filenum_on_date[dt]
            del filenum_on_date[dt]

    if options.debug:
        print('')
        for dt in sorted(filenum_on_date.keys()): print(dt, filenum_on_date[dt])

#input: filenum_on_data already contains regulated directory names.
#input: tofolder to hold the directory structure.
#output: directory structure at the tofolder.
def prep_dirs(tofolder: Path):
    for dt in sorted(filenum_on_date.keys()):
        newfolder = tofolder / dt[0:4] / dt
        if not newfolder.exists():
            os.makedirs(newfolder)
        elif newfolder.is_file():
            raise Exception("Directory conflicts with existing file name.")

def walk_dirs(fromdir, tofolder):
    for folder, subfolders, files in os.walk(fromdir):
        #Do not walk under the destination folder.
        srcfolder = Path(folder)
        #print(folder, tofolder)
        commonfolder = os.path.commonpath([srcfolder, tofolder])
        #print(commonfolder, tofolder)
        if commonfolder and os.path.samefile(commonfolder, tofolder):
            print("skipping ", srcfolder)
            continue
        move_files(srcfolder, tofolder)

if __name__ == "__main__":
    from optparse import OptionParser

    # parse options
    parser = OptionParser()
    parser.add_option('-r', '--recurse', default=False, action="store_true",
                dest='recurse', help="Walk down the directory recursively.")
    parser.add_option('-d', '--debug', default=False, action="store_true",
                dest='debug', help="Turn on debug mode.")
    parser.add_option('-m', '--merge', default=False, action="store_true",
                dest='merge', help="Merge the same files.")
    parser.add_option('-x', '--extension', default='.jpg',
                dest='extension', help="File extension to archive.")
    (options, args) = parser.parse_args()

    print(options)

    if (len(args) > 1):
        fromdir = Path(args[0])
        todir = Path(args[1])
    else:
        fromdir = Path(".")
        todir = Path("/tmp/")

    if options.debug:
        print("args parse result: ", options, fromdir, todir)

    try:
        if not fromdir.exists():
            raise
        if not todir.exists():
            os.makedirs(todir)
    except Exception as e:
        print(e)
        parser.print_help()
        sys.exit(1)

    # arrange file into directories.
    tally_dirs(fromdir, todir)
    prep_dirs(todir)

    move_files(fromdir, todir)
    if options.recurse:
        walk_dirs(fromdir, todir)
