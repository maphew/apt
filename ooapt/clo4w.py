import requests

# main class for osgeo4w-metadata
class O4w:
    # is inherited by Setup, Packages

    # global to the class and all subclasses
    o4wurl     = "http://download.osgeo.org/osgeo4w/"

    archs      = {"x32":"x86", "x64":"x86_64", "x86":"x86", "x86_64":"x86_64" }

    files      = {"installed":"installed.db", "ini": "setup.ini", \
                  "bak":"setup.bak", "conf":"setup.rc"}

    rc_keys    = ['last-cache', 'last-mirror', 'mirrors-lst', \
                  'window-placement', 'last-mode', 'last-menu-name', 'net-method', ]

    ini_keys   = ['sdesc','ldesc','category','requires','version', \
                  'install','license','source']

    install_keys = ['ball','status','version','file_name', \
                    'download_exists','file_list','extracted']

    curr = 'curr'; test = 'test'; prev = "prev"
    ldist = [curr, test, prev]

    # should be set by Setup
    last_mirror = o4wurl
    last_cache = ""

    # we know root (OSGEO4W_ROOT), so we get some more information
    def __init__(self, root):
        self.root = root
        self.setup_dir  = root + "/etc/setup/"
        self.var_dir = root + "/var/"
        env_vars   = {"OSGEO4W_ROOT":root}

    # path to join with package information
    # this should give:
    # F:\gp2go\osgeo4w\var\cache\setup\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f
    def local_pkg_path(self):

        return self.var_dir + "cache/setup/" + self.url2path(self.o4wurl)
            # deleted this, because packages have this
            # + self.archs[arch] + "/release/"
            # see _fullpath version

    # F:\gp2go\osgeo4w\var\cache\setup\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f/x86/release/
    # used with installed packages
    def local_pkg_fullpath(self, arch='x32'):
        if not arch in set(self.archs): return

        return self.var_dir + "cache/setup/" + self.url2path(self.o4wurl) + \
               self.archs[arch] + "/release/"

    # other pathes we should know
    def server_pkg_path(self, arch='x32'):
        if not arch in set(self.archs): return

        return self.o4wurl + self.archs[arch] + "/release/"

    def server_ini_path(self, arch="x32"):
        if not arch in set(self.archs): return

        return self.o4wurl + self.archs[arch] + "/"

    # good old converter for local pathes
    def url2path(self, url):
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