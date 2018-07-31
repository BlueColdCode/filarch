# filarch
Archive image and video files according to the creation timestamp using the multimedia metadata.

Note that currently it only works with JPEG files. 

Usage documentation:

bash$ ./filarch.py --help
Usage: filarch.py [options]

Options:
  -h, --help            show this help message and exit
  -r, --recurse         Walk down the directory recursively.
  -m, --merge           Merge the same files.
  -x EXTENSION, --extension=EXTENSION
                        File extension to archive.

TODO list:
- Support MP4.
- Support MOV.
- Support PNG and other image types.
