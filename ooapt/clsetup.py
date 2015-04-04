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
        self.data = []

        # do an initial config-setup
        self.config = self.setup_dir + O4w.files['conf']

        # read setup_rc here
        if os.path.exists(os.path.normpath(self.config)):
            self.data.append(self.parse_setuprc(self.config))
        else:
            self.data.append({})

        # find mirror-url
        if self.data[0].has_key('last_mirror'):
            O4w.last_mirror = self.data[0]['last_mirror']

        if O4w.last_mirror:
            O4w.mirror = O4w.last_mirror
        else:
            O4w.mirror = o4wurl

        # find cache_dir
        if self.data[0].has_key('last_cache'):
            O4w.last_cache = self.data[0]['last_cache']

        if O4w.last_cache:
            O4w.cache_dir = O4w.last_cache
        else:
            O4w.cache_dir= self.var_dir + "cache/"

        # arch[itecture] has default value

        # find setup.ini
        O4w.setupini_dir = self.local_pkg_path(O4w.cache_dir) + self.archs[self.arch] + "/" \
                                           + self.files['ini']
        # find installed.db
        O4w.installdb_dir = self.setup_dir + self.files['installed']

        # dist is 'curr'

    def setConfigByData(self, data):
        """Use this to overwrite default config parameters, see also getConfigData()"""
        O4w.mirror = data['mirror'] if data.has_key('mirror') else O4w.mirror
        O4w.setupini_dir = data['setupini_dir'] if data.has_key('setupini_dir') else O4w.setupini_dir
        O4w.installdb_dir = data['installdb'] if data.has_key('installdb') else O4w.installdb_dir
        O4w.cache_dir = data['cache_dir'] if data.has_key('cache_dir') else O4w.cache_dir
        O4w.arch = data['arch'] if data.has_key('arch') else O4w.arch
        O4w.dist = data['dist'] if data.has_key('dist') else O4w.dist
        self.root = data['root'] if data.has_key('root') else self.root

    def getConfigData(self):
        """Use this to get config data as a dictionary. Can be written back with setConfigByData()"""
        d = { 'mirror': O4w.mirror,
              'setupini_dir': O4w.setupini_dir,
              'installdb': O4w.installdb_dir,
              'cache_dir': O4w.cache_dir,
              'arch': O4w.arch,
              'dist': O4w.dist,
              'root': self.root }
        return d


    def create(self):
        """if you install from scratch, create() will build the skeleton structure and files"""

        # create dir for setup.ini
        sdir = os.path.dirname(self.setupini_dir)
        # sdir = self.local_pkg_path() + self.archs['x32']
        try:
            os.makedirs(os.path.normpath(sdir))
        except WindowsError as e:
            if not e.errno == 17:
                raise
        # get setup.ini
        # url = self.ow4url + self.archs['x32'] + "/setup.ini.bz2"
        url = self.server_ini_path('x32') + "/setup.ini.bz2"
        # dst = self.setup_dir + "setup.ini.bz2"
        dst = sdir + "/setup.ini.bz2"
        copyme.download(url, dst)
        copyme.bz2uncompress(dst, O4w.setupini_dir)

        # setup.rc
        try:
            os.makedirs(os.path.normpath(self.setup_dir))
        except WindowsError as e:
            if not e.errno == 17:
                raise
        # create config-file setup.rc
        fname = self.setup_dir + "/setup.rc"
        # rcstr = "".join([k + "\n\n" for k in self.rc_keys])
        rcdata = {'last-cache': self.var_dir + "cache/", \
        'last-mirror': self.o4wurl, \
        'mirrors-lst': 'http://download.osgeo.org/osgeo4w/;OSGeo;USA;California', \
        'window-placement': '44,0,0,0,0,0,0,0,1,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,154,1,0,0,4,0,0,0,156,4,0,0,72,2,0,0', \
        'last-mode': 'Advanced', \
        'last-menu-name': 'OSGeo4W', \
        'net-method': 'Direct'}
        rcstr = "".join( ["".join( (str(k), '\n\t' + str(rcdata[k]) + '\n') ) for k in self.rc_keys] )
        try:
            file = open(fname, "wb")
            file.write(rcstr)
            file.close()
        except IOError:
            print '\n*** Error writing: %s' % fname

        # create installed.db
        try:
            file = open (self.installdb_dir, 'w')
            file.write ('INSTALLED.DB 2\n')
            file.close()
        except IOError as e:
            print "Error (#%d):%s:%s" % (e.errno, e.message, e.filename)

    def parse_setuprc(self, fname):
        """reads the config file and returns a dict object"""
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
        """reads available packages from setup.ini, returns a dict"""
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
        """reads in the information on installed packages from installed.db, returns a dict.
        It gives {name: {'ball':..., 'status':...}"""
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
        """Setup files will be loaded and parsed. returns the entire data as list of dict"""

        # availlable from setup.ini: parse to dict
        ini = self.parse_setupini(O4w.setupini_dir)
        c = ini['curr']
        t = ini['test']
        p = ini['prev']
        # one package name may have several dists,
        # we add them here under 'curr'
        for name in c.keys():
            if t.has_key(name):
                c[name]['test'] = t[name]
            if p.has_key(name):
                c[name]['prev'] = p[name]
        # save to list
        self.data.append(c)

        # installed from installed.db, parce to dict
        idb = self.parse_installed(O4w.installdb_dir)
        # save to list
        self.data.append(idb)

        return self.data

if __name__=='__main__':
    root = r"D:\gp2go\dev\apt_oo"
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
    print "Methods (download)", pkg.download()
    print "           (data) ", type(pkg.asData())
