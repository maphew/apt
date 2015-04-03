from clo4w import O4w
import os
import copyme

# inherits O4w for global setting
# is used by: Setup
#### #### #### #### ####

class AptInformation(O4w):
    def __init__(self, root):
        O4w.__init__(self, root)
        self.packages = {}
        self.link = None

    def add(self, name, package):
        # TEST: name, existence, type
        self.pacakges[name] = package

    def addByData(self, name, data):
        pass

    def dataHelper(self, name, data):
        pass

    def getPackage(self, name):
        if self.packages.has_key(name):
            return self.packages[name]

    def getPackageData(self, name):
        pkg = self.getPackage(name)
        if pkg:
            return pkg.asData()

    def getInfo(self, name):
        data = self.getPackageData(name)
        aStr = """----- INFO %s:""" % name
        i = len(aStr)
        for k in self.ini_keys:
            aStr += "\n" + k + ": " + str(data[k] if data.has_key(k) else '')
        aStr += "\n" + "-"*i
        return aStr
#### ####

class AptInstalled(AptInformation):

    def __init__(self, root):
        AptInformation.__init__(self, root)
        self.ref_available = None

    def addByData(self, name, data):
        """use data from setup to add package meta data"""
        # data enhancement !!!
        d = self.dataHelper(name, data)
        if not d: return
        pkg = AptPackageAvailable(name, self)
        pkg.addData(d)
        # store
        self.packages[name] = pkg

    def dataHelper(self, name, data):
        """Turn installed data into AptInstalled format"""
        if not data.has_key(name): return

        ind = dict(data[name])

        ind['version']    = ind['ball'][:-8].replace(name+"-","")
        ind['file_name']  = self.local_pkg_path() + "/" + name + "/" + \
                                                ind['ball']
        ind['download_exists'] = os.path.exists(os.path.normpath(
                                                ind['file_name']))
        ind['file_list']       = self.setup_dir + name + "lst.gz"
        ind['extracted']       = os.path.exists(os.path.normpath(
                                                ind['file_list']))
        ind['name'] = name
        return ind

    def extract(self):
        if self.instd['download_exists']:
            print (self.instd['file_name'], self.list.root)
            # copyme.untar(pkg.instd['file_name'], self.list.root)
#### #####

class AptAvailable(AptInformation):
    def __init__(self, root):
        AptInformation.__init__(self, root)
        self.ref_installed = None

    def addByData(self, name, data):
        """use data from setup/installed.db to add package meta data"""
        # data enhancement !!!
        d = self.dataHelper(name, data)
        if not d: return
        pkg = AptPackageAvailable(name, self)
        pkg.addData(d)
        # store
        self.packages[name] = pkg

    def dataHelper(self, name, data):
        """Turn available data (from setup.ini/setup) into AptAvailable format"""
        if not data.has_key(name): return

        # copy data into avl
        avl = dict(data[name])

        # check keys to split as dictionary
        for key in ['install', 'source']:
            if avl.has_key(key):
                # dict comprehension: d = {key: value for (key, value) in iterable}
                avl[key] = { k:v for (k,v) in \
                           zip(['dir', 'size', 'checksum'], avl[key].split())}
        # split as list
        if avl.has_key('requires'):
            avl['requires'] = avl['requires'].split()
        # add package name
        avl['name'] = name
        return avl

#### #### #### ####

class AptPackage(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

class AptPackageAvailable(AptPackage):
    def __init__(self, name, parent):
        AptPackage.__init__(self, name, parent)
        self.sdesc = ''
        self.ldesc = ''
        self.category = ''
        self.requires = ''
        self.version = ''
        self.install = ''
        self.license = ''
        self.source = ''

    def addData(self, data):
        self.sdesc    = data['sdesc'] if data.has_key('sdesc') else ''
        self.ldesc    = data['ldesc'] if data.has_key('ldesc') else ''
        self.category = data['category'] if data.has_key('category') else ''
        self.requires = data['requires'] if data.has_key('requires') else ''
        self.version  = data['version'] if data.has_key('version') else ''
        self.install  = data['install'] if data.has_key('install') else ''
        self.license  = data['license'] if data.has_key('license') else ''
        self.source   = data['source'] if data.has_key('source') else ''

        if self.install and isinstance(self.install, dict):
            self.install_dir = self.install['dir']
            self.install_size = self.install['size']
            self.install_checksum = self.install['checksum']

        if self.source and isinstance(self.source, dict):
            self.source_dir = self.source['dir']
            self.source_size = self.source['size']
            self.source_checksum = self.source['checksum']

    def asData(self):
        data = {}
        data['sdesc']    = self.sdesc
        data['ldesc']    = self.ldesc
        data['category'] = self.category
        data['requires'] = self.requires
        data['version']  = self.version
        data['install']  = self.install
        data['license']  = self.license
        data['source']   = self.source
        return data

    def download(self):
        print self.parent.o4wurl + self.install_dir, \
              self.parent.root + "/" + self.install_dir
        # copyme.download(self.o4wurl + self.install_dir, self.parent.root + "/" + self.install_dir)
        pass

class AptPackageInstalled(AptPackage):
    def __init__(self, name, parent):
        AptPackage.__init__(self, name, parent)
        self.ball = ""
        self.status = ""
        self.version = ""
        self.file_name = ""
        self.download_exists = ""
        self.file_list = ""
        self.extracted = ""

    def data_helper(self, data):
        pass
    def addData(self, data):
        self.ball      = data['ball'] if data.has_key('ball') else ''
        self.status    = data['status'] if data.has_key('status') else ''
        self.version   = data['version'] if data.has_key('version') else ''
        self.file_name = data['file_name'] if data.has_key('file_name') else ''
        self.download_exists = data['download_exists'] if data.has_key('download_exists') else ''
        self.file_list = data['file_list'] if data.has_key('file_list') else ''
        self.extracted = data['extracted'] if data.has_key('extracted') else ''

    def asData(self):
        data = {}
        data['ball']            = self.ball
        data['status']          = self.status
        data['version']         = self.version
        data['file_name']       = self.file_name
        data['download_exists'] = self.download_exists
        data['file_list']       = self.file_list
        data['extracted']       = self.extracted
        return data

#### #### #### #### ####

#### not used: #### ####
class Packages(O4w):
    def __init__(self, root):
        O4w.__init__(self, root)
        self.curr_pkg = {}
        self.test_pkg = {}
        self.prev_pkg = {}

    def info(self, name, dist='curr'):
        pkg = self.get_package(name,dist)
        if pkg:
            return pkg.info()

    # access the lists
    def get_package(self, name, dist="curr"):
        if dist in ['curr', 'test', 'prev']:
            if dist == 'curr':
                if name in self.curr_pkg: return self.curr_pkg[name]
            if dist == 'test':
                if name in self.test_pkg: return self.test_pkg[name]
            if dist == 'prev':
                if name in self.prev_pkg: return self.prev_pkg[name]

    # load from setups dictionary
    def load(self, pkg_data):
        avail = pkg_data[0]
        instd = pkg_data[1]

        # available packages from setup.ini: av: an available
        for name in avail.keys():
            # build a new Package
            pkg = Package(name,self)
            av = avail[name]

            # if av.has_key('install'):
            #    vals = av['install'].split()
            #    keys = ['dir', 'size', 'checksum']
            #    # dict comprehension: d = {key: value for (key, value) in iterable}
            #    install = {k:v for (k,v) in zip(keys, vals)}
            #    av['install'] = install

            # check keys to split
            for ak in ['install', 'source']:
                if av.has_key(ak):
                    # dict comprehension: d = {key: value for (key, value) in iterable}
                    av[ak] = { k:v for (k,v) in \
                               zip(['dir', 'size', 'checksum'], av[ak].split())}
            if av.has_key('requires'):
                av['requires'] = av['requires'].split()

            # check keys which define a variant dist
            for ak in ['test', "prev"]:
                if av.has_key(ak):
                    # each dist needs a separated pkgv
                    pkgv = Package(name, self)
                    # an available variant: avv
                    avv = dict(av[ak])
                    # an key variant to split
                    for akv in ['install', 'source']:
                        if avv.has_key(akv):
                            avv[akv] = { k:v for (k,v) in \
                               zip(['dir', 'size', 'checksum'], avv[akv].split())}
                    # save the variant dist info
                    pkgv.avail = dict(avv)
                    pkgv.dist = ak
                    # save package in list
                    if   ak=='test': self.test_pkg[name] = pkgv
                    elif ak=='prev': self.prev_pkg[name] = pkgv
                    # change value to True
                    av[ak] = True

            # save the available meta data
            pkg.avail = dict(av)
            pkg.dist = 'curr'
            # save the package
            self.curr_pkg[name]= pkg

        # listed as installed
        # todo: which dist is installed?
        for name in instd.keys():
            if self.curr_pkg[name]:
                pkg = self.curr_pkg[name]   # or test_dict or prev_dict or all
            else:
                raise KeyError("Error in processing setup: installed package not found in setup.ini")

            pkg.instd['ball']            = instd[name]['ball']
            pkg.instd['status']          = instd[name]['status']
            pkg.instd['version']         = instd[name]['ball'][:-8].replace(name+"-","")
            pkg.instd['file_name']       = self.local_pkg_path() + "/" + \
                                                name + "/" + instd[name]['ball']
            pkg.instd['download_exists'] = os.path.exists(os.path.normpath(pkg.instd['file_name']))
            pkg.instd['file_list']       = self.setup_dir + name + "lst.gz"
            pkg.instd['extracted']       = os.path.exists(os.path.normpath(pkg.instd['file_list']))


class Package(object):
    def __init__(self, name, pkglist):
        self.name = name
        self.dist = ""
        self.list = pkglist
        self.avail = {} # meta data through setup.ini
        self.instd = {} # meta data through installed.db

    def info(self, key=None):
        d = {}
        if not key:
            return {"available":self.avail, "installed":self.instd}
        # todo: get key/value for info in avail and instd
        if self.avail.has_key(key): d['available'] = self.avail[key]
        if self.instd.has_key(key): d['installed'] = self.instd[key]
        return d

    def check_version(self):
        if self.instd.has_key('version'):
            return {"installed":self.instd['version'], "available":self.avail['version']}

    def extract(self):
        if self.instd['download_exists']:
            print (self.instd['file_name'], self.list.root)
            # copyme.untar(pkg.instd['file_name'], self.list.root)
#### ####

#### #### #### ####


if __name__ == '__main__':
    # create a nonsense package
    ap = AptPackageAvailable("oma", None)
    # more nonsense
    d = {'sdesc': "ticket to ride", 'ldesc': "ticket to ride, but she don't care", 'category' : "Beatles", 'requires': "Vox, Hofner, Rickenbacker", 'version': '1.0.0', 'install': "ticket_to_ride.tar.gz2 1000 8165553b6b72338a53105301269aee92", 'license': "Lucy in the sky", 'source': "paul_john_george_ringo.tar.gz2, 100, 8db10fd3782fc99a4bf69ecdbe2c3747"}
    ap.addData(d)
    # this one's install wasn't split
    print ap.ldesc, ap.requires, ap.source, ap.install
    # there is no property "install_dir"
    try:
        print ap.install_dir
    except:
        print "NO INSTALL_DIR"
        pass

    # this is done through list's addByData
    data = {'oma':d} # normally all packages are here
    # build a package list for available packages, listed in setup.ini
    apl = AptAvailable("/Abbey/Road")
    # adding package oma from data
    apl.addByData('oma', data)
    pkg = apl.getPackage('oma')
    # now we have extra information
    print "install_dir:  ", pkg.install_dir