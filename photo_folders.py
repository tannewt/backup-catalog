import pathlib
import sqlite3

db = sqlite3.connect("test.db")

cur = db.cursor()

directories = {}
for rfn, size, sha256, mimetype, mtime in cur.execute("SELECT * FROM files WHERE mimetype LIKE 'image/%'"):
    rfn = pathlib.Path(rfn)
    p = rfn.parent
    if p not in directories:
        directories[p] = 0
    directories[p] += 1

for rfn, count in sorted(directories.items(), key=lambda x: x[1]):
    print(count, rfn)
