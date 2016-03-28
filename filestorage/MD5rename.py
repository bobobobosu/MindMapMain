import hashlib
import PyPDF2
import time
import win32clipboard

BLOCKSIZE = 65536
hasher = hashlib.md5()

import os

win32clipboard.OpenClipboard()
data = win32clipboard.GetClipboardData()
win32clipboard.CloseClipboard()
print (data)

for root, dirs, files in os.walk("../_pdfDATA"):
    for file in files:
        if file.endswith(""):
            #print(os.path.join(root, file))
            #os.system(str('start '+os.path.join(root, file)))
            #time.sleep(1)
            with open(os.path.join(root, file), 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
                #print(hasher.hexdigest())
            try:
                os.rename(os.path.join(root, file),
                          os.path.join(root, hasher.hexdigest() + os.path.splitext(os.path.join(root, file))[1]))
            except:
                os.remove(os.path.join(root, hasher.hexdigest() + os.path.splitext(os.path.join(root, file))[1]))
