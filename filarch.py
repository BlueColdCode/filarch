#!/usr/bin/env python3

import sys, os
import datetime
import filecmp
from pathlib import PurePath, Path
from PIL import Image
import shutil
import string

options = {'recurse': False, 'merge': False, 'extension': '.jpg'}
filenum_on_date = {}

#input: date of the file creation.
#input: seqno: the sequence number of the file created at the same moment.
# return string filename based on date.
def filename_on_date(dt, seqno = 0):
    pref = '1' if dt.strftime('%Y') == '19' else '2'
    newfilename = pref + dt.strftime('%y') + ('%X' % dt.month) + dt.strftime('%d_') +\
                  ('%c' % list(string.ascii_uppercase)[dt.hour]) + ('%.2d' % dt.minute) + ('%.2d' % (dt.second + seqno)) +\
                  options.extension
    return newfilename

def locate_dir(createdate: datetime):
    cdate = createdate.strftime('%Y%m%d')
    tdate = None
    for dt in sorted(filenum_on_date.keys()):
        if tdate == None: tdate = dt
        if dt <= cdate:
            tdate = dt
        else:
            break

    if tdate == None:
        raise Exception("Destination directory not found for " + cdate)

    return tdate

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
            weekday = createdate.date().isoweekday() - 1
            folderdate = createdate.date() - datetime.timedelta(days=weekday)
            destfolder = Path(tofolder) / folderdate.strftime('%Y') / locate_dir(createdate)

            # make up the new file name.
            newfilename = filename_on_date(createdate)
            newfile = destfolder / newfilename

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

#input: dirname with all the files.
#output: directory names and corresponding file number in each.
def tally_dirs(dirname):
    for folder, subfolders, files in os.walk(dirname):
        for filename in os.listdir(folder):
            if not PurePath(filename).suffix.lower() == options.extension: continue
            try:
                oldfile = Path(folder) / filename

                # figure out the destination directory
                ftags = Image.open(oldfile)._getexif()
                # some image files do not have EXIF tags.
                if ftags is None: continue
                createtimestamp = ftags[36867]
                createdate = datetime.datetime.strptime(createtimestamp, '%Y:%m:%d %H:%M:%S').date().strftime("%Y%m%d")

                #print(oldfile, "created on " + createdate)

                if filenum_on_date.get(createdate) == None:
                    filenum_on_date[createdate] = 1
                else:
                    filenum_on_date[createdate] += 1
            except Exception as e:
                print(e)
                pass
    dates = sorted(filenum_on_date.keys())
    #for dt in dates: print(dt, filenum_on_date[dt])

    collector_dt = None
    for dt in dates:
        # starting point to count
        if collector_dt == None or collector_dt[0:6] != dt[0:6]:
            collector_dt = dt
            continue

        if filenum_on_date[collector_dt] + filenum_on_date[dt] < 100:
            filenum_on_date[collector_dt] += filenum_on_date[dt]
            del filenum_on_date[dt]

    #print('')
    dates = sorted(filenum_on_date.keys())
    #for dt in dates: print(dt, filenum_on_date[dt])

#input: filenum_on_data already contains regulated directory names.
#input: destfolder to hold the directory structure.
#output: directory structure at the destfolder.
def prep_dirs(destfolder: Path):
    for dt in sorted(filenum_on_date.keys()):
        newfolder = destfolder / dt[0:4] / dt
        if not newfolder.exists():
            os.makedirs(newfolder)
        elif newfolder.is_file():
            raise Exception("Directory conflicts with existing file name.")

def walk_dirs(dirname, destfolder):
    for folder, subfolders, files in os.walk(dirname):
        #Do not walk under the destination folder.
        srcfolder = Path(folder)
        #print(folder, destfolder)
        commonfolder = os.path.commonpath([srcfolder, destfolder])
        #print(commonfolder, destfolder)
        if commonfolder and os.path.samefile(commonfolder, destfolder):
            print("skipping ", srcfolder)
            continue
        move_files(srcfolder, destfolder)

if __name__ == "__main__":
    from optparse import OptionParser

    # parse options
    parser = OptionParser()
    parser.add_option('-r', '--recurse', default=False, action="store_true",
                dest='recurse', help="Walk down the directory recursively.")
    parser.add_option('-m', '--merge', default=False, action="store_true",
                dest='merge', help="Merge the same files.")
    parser.add_option('-x', '--extension', default='.jpg',
                dest='extension', help="File extension to archive.")
    (options, args) = parser.parse_args()

    print(options)

    if (len(args) > 1):
        dirname = Path(args[0])
        destname = Path(args[1])
    else:
        dirname = Path(".")
        destname = Path("/tmp/")

    #print(options, dirname, destname)

    try:
        if not dirname.exists():
            raise
        if not destname.exists():
            os.makedirs(destname)
    except Exception as e:
        print(e)
        parser.print_help()
        sys.exit(1)

    # arrange file into directories.
    tally_dirs(dirname)
    prep_dirs(destname)

    move_files(dirname, destname)
    if options.recurse:
        walk_dirs(dirname, destname)
