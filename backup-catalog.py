import sys
import pathlib
import time
import sqlite3
import hashlib
import mimetypes

db = sqlite3.connect(sys.argv[2])

cur = db.cursor()
new = False
root = pathlib.Path(sys.argv[1])
try:
    cur.execute("CREATE TABLE directories(filepath TEXT PRIMARY KEY, mtime INTEGER, scan_mtime INTEGER)")
    cur.execute("INSERT INTO directories VALUES (?, ?, ?)", (".", root.stat().st_mtime_ns, 0))
    cur.execute("CREATE TABLE files(filepath TEXT PRIMARY KEY, size INTEGER, sha256 BLOB, mimetype TEXT, mtime INTEGER)")
    db.commit()
    new = True
except sqlite3.OperationalError as e:
    print("sqlite3 error", e)
    pass
# use system_profiler -json -detailLevel full SPUSBDataType to get hard drive
# (usb) serial number

# cur.execute("UPDATE directories SET scan_mtime = 0")

print("listing")
i = 0
while True:
    res = cur.execute("SELECT filepath FROM directories WHERE mtime > scan_mtime LIMIT 1")
    res = res.fetchone()
    if res is None:
        break
    d = root / res[0]
    if not d.exists():
        mt = time.time_ns()
        cur.execute("UPDATE directories SET scan_mtime = ? WHERE filepath = ?", (mt, res[0]))
        continue
    ds = d.stat()
    for fn in d.iterdir():
        rfn = fn.relative_to(root)
        if i % 100 == 0:
            print(i, rfn)
        i += 1
        if fn.is_dir():
            try:
                mtime_ns = fn.stat().st_mtime_ns
                if mtime_ns < 0:
                    mtime_ns = 1
                cur.execute("INSERT INTO directories VALUES (?, ?, ?)", (str(rfn), mtime_ns, 0))
                print("insert dir", rfn)
            except sqlite3.IntegrityError:
                cur.execute("UPDATE directories SET mtime = ? WHERE filepath = ?", (fn.stat().st_mtime_ns, str(rfn)))
        elif fn.is_file():
            mimetype, _ = mimetypes.guess_type(fn)
            s = fn.stat()
            data = (str(rfn), s.st_size, None, mimetype, s.st_mtime_ns)
            try:
                cur.execute("INSERT INTO files VALUES(?, ?, ?, ?, ?)", data)
            except sqlite3.IntegrityError:
                pass
        db.commit()
    mt = ds.st_mtime_ns
    cur.execute("UPDATE directories SET mtime = ?, scan_mtime = ? WHERE filepath = ?", (mt, mt, res[0]))
    db.commit()

print("hashing")
i = 0
while True:
    res = cur.execute("SELECT filepath FROM files WHERE sha256 IS NULL LIMIT 1")
    res = res.fetchone()
    if res is None:
        break
    fn = root / res[0]
    if i % 100 == 0:
        print(i, res[0])
    i += 1
    try:
        f = fn.open('rb')
    except OSError:
        continue
    if hasattr(hashlib, "file_digest"):
        sha256 = hashlib.file_digest(f, "sha256").digest()
    else:
        hasher = hashlib.sha256()
        buf = f.read(hasher.block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(hasher.block_size)
        sha256 = hasher.digest()
    f.close()
    cur.execute("UPDATE files SET sha256 = ? WHERE filepath = ?", (sha256, res[0]))
    db.commit()
