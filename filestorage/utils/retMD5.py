import hashlib
import os

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return os.path.split(os.path.basename(fname))[0]+hash_md5.hexdigest()+os.path.splitext(os.path.split(fname)[1])[1]

