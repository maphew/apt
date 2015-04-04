import requests

# main class for osgeo4w-metadata
class O4w:
    """You may never instanciate this class, as it is inherited by othre classes.
    You'll find a global part to distribute variable changes between classes.
    Change them through the class identifier O4w, and all instances will have this new value."""
    # is inherited by Setup, Packages

    ### Here comes the global part: global to the class and all subclasses ###


    # change this through the class identifier O4w, and all instances will have this new value
    # for example: O4w.mirror = "..."

    o4wurl     = "http://download.osgeo.org/osgeo4w/"

    archs      = {"x32":"x86", "x64":"x86_64", "x86":"x86", "x86_64":"x86_64" }

    files      = {"installed":"installed.db", "ini": "setup.ini", \
                  "bak":"setup.bak", "conf":"setup.rc"}

    rc_keys    = ['mirrors-lst', 'window-placement',  \
                  'last-mode', 'last-mirror', 'net-method', \
                  'last-cache', 'last-menu-name' ]

    ini_keys   = ['sdesc','ldesc','category','requires','version', \
                  'install','license','source']

    install_keys = ['ball','status','version','file_name', \
                    'download_exists','file_list','extracted']

    curr = 'curr'; test = 'test'; prev = "prev"
    ldist = [curr, test, prev]

    # default values for Setup
    # add all that what could be changed by user on command line
    last_mirror = o4wurl
    mirror = o4wurl
    last_cache = ""
    setupini_dir = ""
    installdb_dir = ""
    cache_dir = ""
    arch = "x86"
    dist = "curr"
    # Class Setup manages this


    ### Here comes the class methods part ###

    # we know root (OSGEO4W_ROOT), so we get some more information
    def __init__(self, root):
        self.root = root
        self.setup_dir  = root + "/etc/setup/"
        self.var_dir = root + "/var/"
        env_vars   = {"OSGEO4W_ROOT":root}

    # path to join with package information
    # this should give:
    # F:\gp2go\osgeo4w\var\cache\setup\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f/
    #
    def local_pkg_path(self, cache=''):
        """return the path, where downloads are stored, uses a representation of the url"""

        # changed cache/setup to just cache
        if not cache:
            cache = self.var_dir + "cache/"

        # or should we use 'mirror' instead of default url 'o4wurl'
        return  cache + self.url2path(self.mirror)
            # deleted this, because packages have this
            # + self.archs[arch] + "/release/"
            # see _fullpath version

    # F:\gp2go\osgeo4w\var\cache\setup\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f/x86/release/
    # used with installed packages
    #
    def local_pkg_fullpath(self, cache='', arch='x32'):
        """full path where packages are stored, normally /var/.../release/"""
        if not arch in set(self.archs): return

        return self.local_pkg_path(cache) +  self.archs[arch] + "/release/"

    # other pathes we should know
    def server_pkg_path(self, arch='x32'):
        """Use this return values + packagename + tarfile for downloads"""
        if not arch in set(self.archs): return
        # use 'mirror' here?
        return self.mirror + self.archs[arch] + "/release/"

    def server_ini_path(self, arch="x32"):
        """Use this to access setup.ini or setup.ini.bz2"""
        if not arch in set(self.archs): return
        # use 'mirror' here?
        return self.mirror + self.archs[arch] + "/"

    # good old converter for local pathes
    def url2path(self, url):
        """Returns a good representation of an url as a valid path name"""
        return requests.utils.quote(url, '').lower() + "/"

# test
if __name__ == '__main__':
    o = O4w('d:/amr/osgeo4w')
    # o.local_pkg_path()
    print 'o.var_dir', o.var_dir
    print 'o.o4wurl', o.o4wurl
    print "Server pkg path", o.server_pkg_path()
    print 'o.archs[x32]', o.archs['x32']
    print o.var_dir + "cache/setup/" + o.url2path(o.o4wurl) + \
            o.archs['x32'] + "/release/"
    print "Server ini path", o.server_ini_path()
    print "short", o.local_pkg_path()
    print "long", o.local_pkg_fullpath()