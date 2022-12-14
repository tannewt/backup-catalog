import pathlib
import os
import time
import sys

root = pathlib.Path(sys.argv[1])

for fn in root.glob("**/*.mp4"):
    ts = time.mktime(time.strptime(fn.name, "%Y_%m_%d_%H_%M_%S.mp4"))
    print(fn, ts)
    os.utime(fn, (ts, ts))
