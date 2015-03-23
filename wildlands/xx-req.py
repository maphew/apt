import sys
import requests
srcFile = 'http://download.osgeo.org/osgeo4w/x86/release/iconv/iconv-1.9.1-1.tar.bz2'
dstFile = r'B:\o4w\var\cache\setup\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86\release\iconv\iconv-1.9.1-1.tar.bz2'

# fetch header, without downloading whole file
# http://stackoverflow.com/questions/14270698/get-file-size-using-python-requests-while-only-getting-the-header
r = requests.head(srcFile)

print 'Status code:', r.status_code

for k in r.headers:
    print '%s:%s' % (k, r.headers[k])


# save to disk, with progress indicator
# http://stackoverflow.com/questions/14114729/save-a-file-using-the-python-requests-library
# http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads/
with open(dstFile, 'wb') as handle:
    r = requests.get(srcFile, stream=True)
    total_length = int(r.headers.get('content-length'))
    dl = 0
    for block in r.iter_content(1024):
        dl += len(block)
        if not block:
            break
        handle.write(block)
        done = int(50 * dl / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
        sys.stdout.flush()
