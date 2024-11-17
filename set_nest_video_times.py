import pathlib
import os
import time
import datetime
import sys

root = pathlib.Path(sys.argv[1])

offset = datetime.timedelta(hours=8)

for fn in root.glob("**/*.mp4"):
    ts = time.mktime(time.strptime(fn.name, "%Y_%m_%d_%H_%M_%S.mp4"))
    ts = datetime.datetime.fromtimestamp(ts) - offset
    print(fn, ts)
    ts = ts.timestamp()
    os.utime(fn, (ts, ts))
