import os
import sys
import copyme
import bz2
from clo4w import O4w
from clpackages import \
    AptInstalled, AptAvailable, AptPackageAvailable, AptPackageInstalled
debug = False

class Setup(O4w):
    def __init__(self, root):
        O4w.__init__(self, root)
        self.data = None

    def create(self):
        # create dir
        try:
            os.makedirs(os.path.normpath(self.setup_dir))
        except WindowsError as e:
            if not e.errno == 17:
                raise
        # load setup.ini
        url = self.ow4url + self.archs['x32'] + "/setup.ini.bz2"
        dst = self.setup_dir + "setup.ini.bz2"
        copyme.download(url, dst)
        fname = self.setup_dir + "/setup.ini"
        copyme.bz2uncompress(dst, fname)

        # create config-file setup.rc
        fname = self.setup_dir + "/setup.rc"
        rcstr = "".join([k + "\n\n" for k in self.rc_keys])
        try:
            file = open(fname, "wb")
            file.write(rcstr)
            file.close()
        except IOError:
            print '\n*** Error writing: %s' % fname

        # create installed.db
        fname = self.setup_dir + self.files["installed"]
        try:
            file = open (fname, 'w')
            file.write ('INSTALLED.DB 2\n')
            file.close()
        except IOError as e:
            print "Error (#%d):%s:%s" % (e.errno, e.message, e.filename)

    def parse_setuprc(self, fname):
        """returns a dict object"""
        d = {}

        default_keys = self.rc_keys
        try:
            f = open(fname,'r')
            for line in f.readlines():
                if not line.startswith('\t'):
                    key = line.strip()
                    # print 'key:', line
                else:
                    value = line.strip()
                    # print 'value:', line
                    d[key] = value
            f.close()

        except IOError:
            print "Couldn't open %s, setting empty" % fname
            for k in default_keys:
                d[k] = None

        if debug == True:
            print '\n---- DEBUG: %s ----' % sys._getframe().f_code.co_name
            for k,v in d.items():
                print '%s:\t%s' % (k, v)
            print '-' * 40
        return d

    def parse_setupini(self, fname):
        # changed string.method to method calls on string instances
        dists = {'test': {}, 'curr': {}, 'prev': {}}

        fname = os.path.normpath(fname)
        fi = open(fname, "rb").read()
        chunks = fi.split('\n\n@ ')
        print "chunks:", len(chunks)
        for i in chunks[1:]:
            lines = i.split('\n')
            name = lines[0].strip()
            if debug and verbose:
                print 'package: ' + name
            packages = dists['curr']
            records = {'sdesc': name}
            j = 1
            while j < len(lines) and lines[j].strip():
                if debug and verbose:
                    print 'raw: ' + lines[j]
                if lines[j][0] == '#':
                    j = j + 1
                    continue

                elif lines[j][0] == '[':
                    if debug and verbose:
                        print 'dist: ' + lines[j][1:5]
                    packages[name] = records.copy()
                    packages = dists[lines[j][1:5]]
                    j = j + 1
                    continue

                # split "field: value record for field" into dict record
                # e.g. "category: Libs Commandline_Utilities"
                #   --> {'category': 'Libs Commandline_Utilities'}
                try:
                    key, value = [s.strip() for s in lines[j].split(':',1)]
                    # map(string.strip,
                    #      string.split(lines[j], ': ', 1))
                except:
                    print lines[j]
                    raise TypeError('urg')

                #strip outer quotes?
                if value[0] == '"' and value.find('"', 1) == -1:
                    while 1:
                        j = j + 1
                        value += lines[j]
                        if lines[j].find('"') != -1:
                            break

                records[key] = value
                j = j + 1
            packages[name] = records
        return dists

    def parse_installed (self, fname):
        # new! data structure
        # installed is now : {name: {'ball':..., 'status':...}
        # installed = {0:{}}
        installed = {}
        fdb = open (fname, 'rb')
        db_magic = fdb.readline()
        for line in fdb:
            name, ball, status = line.split()
            # was installed[int (status)][name] = ball
            installed[name] = {'ball':ball, 'status':status}
            # strange 0:{}
        return installed

    def load_files(self):
        self.data = []

        fname = self.setup_dir + self.files['conf']
        self.data.append(self.parse_setuprc(fname))

        if self.data[0].has_key('last_mirror'):
            O4w.last_mirror = self.data[0]['last_mirror']

        if self.data[0].has_key('last_cache'):
            O4w.last_cache = self.data[0]['last_cache']


        fname = self.setup_dir + self.files['ini']
        # now has dists
        ini = self.parse_setupini(fname)
        curr = ini['curr']
        test = ini['test']
        prev = ini['prev']
        for name in curr.keys():
            if test.has_key(name):
                curr[name]['test'] = test[name]
            if prev.has_key(name):
                curr[name]['prev'] = prev[name]

        self.data.append(curr)

        fname = self.setup_dir + self.files['installed']
        idb = self.parse_installed(fname)
        self.data.append(idb)

        return self.data

if __name__=='__main__':
    root = r"d:\gp2go\osgeo4w"
    apt_setup = Setup(root)
    setup_data = apt_setup.load_files()

    avail_list = AptAvailable(root)
    for name in setup_data[1]:
        avail_list.addByData(name, setup_data[1])

    instd_list = AptInstalled(root)
    for name in setup_data[2]:
        instd_list.addByData(name, setup_data[2])

    print avail_list.getInfo('gdal')
    pkg =avail_list.getPackage('gdal')
    print "from pkg", pkg.parent.server_pkg_path()
    print "from list", avail_list.server_pkg_path()
    print "Package properties", pkg.source_dir
    print "                  ", pkg.install_dir
    print "Methods (disabled)", pkg.download()
    print "                  ", type(pkg.asData())
