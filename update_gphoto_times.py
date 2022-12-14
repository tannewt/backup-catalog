import os
import pathlib
import sys
import sqlite3
import time

root = pathlib.Path(sys.argv[1])

db = sqlite3.connect(sys.argv[2])

years = []

for fn in root.iterdir():
    if fn.is_dir():
        years.append(int(fn.name))
        continue

print(years)

for fn in root.iterdir():
    if fn.is_dir():
        continue
    print(fn)
    cur = db.cursor()
    cur.execute("SELECT creation_time, camera_model FROM photos WHERE filename = ?", (fn.name,))
    results = cur.fetchall()
    t = None
    for row in results:
        print(row)
        ts = time.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        if ts.tm_year not in years:
            continue
        if t is None:
            t = ts
        elif t != ts:
            # Multiple times
            t = None
            raise RuntimeError()

    if t:
        t = time.mktime(t)
        os.utime(fn, (t, t))

    print()
