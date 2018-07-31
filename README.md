# filarch

Archive image and video files according to the creation timestamp using the multimedia metadata. It requires Python 3 and above, and works on Windows, MacOS, Linux platforms.

The benefits are to archive IMG files into a directory hierarchy according to year/ymd two level structure, and to name each file according to the timestamp in year-month-day-hour-minute-second format for easy retrieval. It also compares IMG files with the same timestamp, and merges them to save time, disk space and image retrieval.

A little history of this project -- I had been doing this for years manually, and finally got time to automate this process. Use it at your own risk.

Note that currently it only supports JPEG files.

# Usage

bash$ ./filarch.py --help

Usage: filarch.py [options]

Options:
  -h, --help            show this help message and exit
  -r, --recurse         Walk down the directory recursively.
  -m, --merge           Merge the same files.
  -x EXTENSION, --extension=EXTENSION
                        File extension to archive.

# Examples

- Copy JPEG files from external HD to local HD:

python3 filarch.py -r -m -x .jpg D:\DCIM C:\Pictures
...
D:\\DCIM\\xyz.jpg  >  C:\\Pictures\\2018\\20180608\\218608_D2436.jpg
...

- Restructure existing JPEG files on the local HD:

python3 filarch.py -r C:\Pictures C:\Archive\Pictures

# TODO list

- Support MP4.
- Support MOV.
- Support PNG and other image types.
