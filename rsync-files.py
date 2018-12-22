#!/usr/bin/env python3


import os
import subprocess

for i in ['Documents', 'Pictures', 'Videos']:
   cmd = "rsync -av /cygdrive/c/Users/username/" + i + "/*" + " " + "/cygdrive/e/" + i + '/'
   print(cmd, flush = True)
   os.system(cmd)

