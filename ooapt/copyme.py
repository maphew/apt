import os
import sys
import shutil as s
import tarfile
import zipfile
import bz2
from datetime import datetime, timedelta
# import urllib2
import requests
debug = False

class CopyError(Exception):
    def __init__(self, errors):
        self.message = ", ".join(errors)
    def __str__(self):
        return repr(self.message)

def unzip(src, dst):
    lst = []
    try:
        dst = os.path.normpath(dst)
        if not os.path.exists(dst):
            os.makedirs(dst)

        os.chdir(dst)
        src = os.path.normpath(src)
        zip = zipfile.ZipFile(src, "r")
        lst = zip.namelist()
        zip.extractall()
        zip.close()

    except zipfile.BadZipfile as e:
        print "Zip error. Couldn't open zip file:", src

    except IOError as e:
        print "I/O-Error while extracting", \
              os.path.basename(src), \
              "({0}): {1}".format(e.errno, e.strerror)

    return lst

def unzip_filter(src, dst, afilter):
    """filter out unwanted parts of filenames in zip-files. Uses
    member.replace(afilter,"")
    !!untested!!"""
    # unzip with file-handles
    with zipfile.ZipFile(src) as zip:
        lst = []
        for member in zip.namelist():
            filename = member.replace(afilter,"")
            # skip root
            if not filename or filename == "/":
                continue

            lst.append(filename)

            # make directories
            if filename[-1] == "/":
                try:
                    n = os.path.join(dst,filename)
                    os.makedirs(n)
                except OSError as e:
                    if WindowsError is not None and isinstance(e, WindowsError):
                        # Makedirs fails on existing dirs
                        pass
                continue

            # copy file (taken from zipfile's extract)
            source = zip.open(member)
            target = file(os.path.join(dst, filename), "wb")
            with source, target:
                s.copyfileobj(source, target)
    # end: unzip with file-handles
    return lst

def untar(src, dst):
    lst = []
    try:
        dst = os.path.normpath(dst)
        if not os.path.exists(dst):
            os.makedirs(dst)
        os.chdir(dst)
        tar = tarfile.open(src,'r')
        lst = tar.getnames()
        tar.extractall()
        tar.close()

    except tarfile.TarError as e:
        print "Tar error({0}): {1}".format(e.errno, e.strerror)

    except IOError as e:
        print "I/O-Error while extracting", \
              os.path.basename(src), \
              "({0}): {1}".format(e.errno, e.strerror)
    return lst

def copylist(src, lst, dst):
    """copy setup files in src/'lst' to dir 'dst'"""

    for f in lst:
        ff = os.path.normpath(src + "/" + f)
        try:
            if os.path.isdir(ff):
                dd = os.path.normpath(dst + "/" + f)
                copytree(ff, dd )
            elif os.path.isfile(ff):
                copy2(ff, dst)
        except IOError as e:
            print e.message, e.errno, e.filename
        except OSError as e:
            if WindowsError is not None and isinstance(e, WindowsError):
                # Copying file access times may fail on Windows
                pass
        except CopyError as e:
            # this comes from copytree
            print e.message
    return

def copy2(src, dst):
    src = os.path.normpath(src)
    dst = os.path.normpath(dst)
    s.copy2(src, dst)

def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    src = os.path.normpath(src)
    dst = os.path.normpath(dst)

    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    errors = []

    try:
        os.makedirs(dst)
    except OSError as e:
        if WindowsError is not None and isinstance(e, WindowsError):
            # Makedirs fails on existing dirs
            pass
        else:
            errors.append((src, dst, e.message))

    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                s.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Exception as e:
            errors.extend(e.message)
        except EnvironmentError as e:
            errors.append((srcname, dstname, e.message))
    try:
        s.copystat(src, dst)
    except OSError as e:
        if WindowsError is not None and isinstance(e, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.append((src, dst, e.message))
    if errors:
        print "error: ", errors
        raise CopyError(errors)
def url_time_to_datetime(s):
    ''' Convert "last-modified" string time from a web server header to a python
        datetime object.

        Assumes the string looks like "Fri, 27 Mar 2015 08:05:42 GMT". There is
        no attempt to use locale or similar, so the function is'nt very robust.
    '''
    return datetime.strptime(s, '%a, %d %b %Y %X %Z')

def bz2uncompress(bz2File, dst=""):

    bz2File = os.path.normpath(bz2File)

    try:
        uncompressedData = bz2.BZ2File(bz2File).read()
    except Exception as e:
        print e.message
        raise IOError('\n*** Error decompressing: %s' % bz2File)
    # fname = self.setup_dir + "/setup.ini"
    if not dst:
        dst = os.path.splitext(bz2File)[0]
    else:
        dst = os.path.normpath(dst)

    try:
        os.makedirs(os.path.dirname(dst))
    except OSError as e:
        if WindowsError is not None and isinstance(e, WindowsError):
            # Makedirs fails on existing dirs
            pass
        else:
            errors.append((src, dst, e.message))

    try:
        file = open(dst, "wb")
        file.write(uncompressedData)
        file.close()
    except:
        raise IOError('\n*** Error decompressing: %s' % dst)

def download(url, dstFile):
    r = requests.head(url)
    if not r.ok:
        print 'Problem getting %s\nServer returned "%s"' % (url, r.status_code)
        return r.status_code

    url_time = url_time_to_datetime(r.headers['last-modified'])
    if os.path.exists(dstFile):
        file_time = datetime.utcfromtimestamp(os.path.getmtime(dstFile))
    else:
        file_time = datetime(1970, 1, 1)

    if url_time <= file_time:
        print "Skipping download - url modified time isn't newer than local file"
        print dstFile
        return dstFile

    if not os.path.exists(os.path.dirname(dstFile)):
        os.makedirs(os.path.dirname(dstFile))

    with open(dstFile, 'wb') as f:
        r = requests.get(url, stream=True)
        total_length = int(r.headers.get('content-length'))
        block_size = 1024
        down_bytes = 0
        for block in r.iter_content(block_size):
            down_bytes += len(block)
            if not block:
                break
            f.write(block)
            down_stat(down_bytes, total_length)
        if not r.ok:
            print 'Problem getting %s\nServer returned "%s"' % (srcFile, r.status_code)
            return r.status_code

    # maintain server's file timestamp
    tstamp = datetime_to_unixtime(url_time)
    os.utime(dstFile, (tstamp, tstamp))
    if debug:
        print '\tFile timestamp:\t', datetime.utcfromtimestamp(tstamp)

    print 'Saved', dstFile
    return dstFile

def datetime_to_unixtime(dt, epoch=datetime(1970,1,1)):
    ''' Convert a datetime object to unix UTC time (seconds since beginning).

        Adapted from http://stackoverflow.com/questions/8777753/converting-datetime-date-to-utc-timestamp-in-python/

    It wants `from __future__ import division`, but that caused issues in other
    functions, automatically coverting what used to produce integers into floats
    (e.g. "50/2"). It seems to be safe to not use it, but leaving this note just
    in case...
    '''
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

def down_stat(downloaded_size, total_size):
    ''' Report download progress in bar, percent, and bytes.

        Each bar stroke '=' is approximately 2%

        Adapted from
            http://stackoverflow.com/questions/51212/how-to-write-a-download-progress-indicator-in-python
            http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
    '''
    percent = int(100 * downloaded_size/total_size)
    bar = int(percent/2)

    if not 'last_percent' in vars(down_stat):
        down_stat.last_percent=0 #Static var to track percentages so we only print N% once.

    if percent > 100: # filesize usually doesn't correspond to blocksize multiple, so flatten overrun
        percent = 100
        down_stat.last_percent=0

    if percent > down_stat.last_percent:
        msg = '\r[{:<50}] {:>3}% {:,}'.format('=' * bar, percent, downloaded_size)
        sys.stdout.write(msg)
        sys.stdout.flush()
    down_stat.last_percent=percent

    if percent == 100:
        print '' #stop linefeed suppression

# test
if __name__=='__main__':
    download("http://download.osgeo.org/osgeo4w/x86/setup.ini.bz2", "./setup.ini.bz2")
    bz2uncompress("./setup.ini.bz2")