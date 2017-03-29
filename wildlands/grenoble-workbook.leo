<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="maphew.20140920000632.1627"><vh>Startup</vh>
<v t="maphew.20140920000632.1628"><vh>@button make-sphinx</vh></v>
<v t="maphew.20140920000632.1629"><vh>@settings</vh>
<v t="maphew.20140920000632.1630"><vh>@string target_language = rest</vh></v>
<v t="maphew.20140920000632.1631"><vh>For rst3 command</vh>
<v t="maphew.20140920000632.1632"><vh>@bool rst3_call_docutils = True</vh></v>
<v t="maphew.20140920000632.1633"><vh>@bool rst3_write_intermediate_file = True</vh></v>
<v t="maphew.20140920000632.1634"><vh>@string rst3_write_intermediate_extension = .txt</vh></v>
</v>
</v>
</v>
<v t="maphew.20140920000632.1691" a="E"><vh>apt</vh>
<v t="maphew.20140922213912.1720" a="E"><vh>by flow</vh>
<v t="maphew.20140922213912.1721" a="E"><vh>Setup</vh>
<v t="maphew.20140927121126.1789"><vh>INSTALLED.DB</vh></v>
<v t="maphew.20100223163802.3732"><vh>setup</vh></v>
<v t="maphew.20100223163802.3764"><vh>write_installed</vh></v>
<v t="maphew.20100223163802.3733"><vh>update</vh></v>
</v>
</v>
<v t="maphew.20170329101849.1" a="E"><vh>@path b:/code/apt</vh>
<v t="maphew.20150327024628.2" a="E"
expanded="maphew.20100308085005.1380,"><vh>@file apt.py</vh></v>
<v t="maphew.20140927120559.1738" a="E"><vh>@path wildlands</vh>
<v t="maphew.20170329105335.1" a="E"><vh>@auto apt-setup.py</vh></v>
<v t="maphew.20130126213204.1603"><vh>@file apt-skeleton.py</vh></v>
<v t="maphew.20140920004020.1709"><vh>@auto clapt.py</vh></v>
<v t="maphew.20140927121126.1730"><vh>@auto setup.py</vh></v>
<v t="maphew.20140927121126.1736"><vh>@auto dapt.py</vh></v>
</v>
</v>
</v>
<v t="maphew.20170329101925.1"><vh>Recovered Nodes</vh>
<v t="maphew.20170329101925.2"><vh>Recovered node "setup" from @file apt.py</vh>
<v t="maphew.20170329101925.3"><vh>old:setup</vh></v>
<v t="maphew.20170329101925.4"><vh>new:setup</vh></v>
</v>
<v t="maphew.20170329101925.5"><vh>Recovered node "update" from @file apt.py</vh>
<v t="maphew.20170329101925.6"><vh>old:update</vh></v>
<v t="maphew.20170329101925.7"><vh>new:update</vh></v>
</v>
<v t="maphew.20170329101925.8"><vh>Recovered node "write_installed" from @file apt.py</vh>
<v t="maphew.20170329101925.9"><vh>old:write_installed</vh></v>
<v t="maphew.20170329101925.10"><vh>new:write_installed</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="maphew.20100223163802.3732">def setup(target):
    '''Create skeleton Osgeo4W folders and setup database environment'''
    if not bits:
        sys.stderr.write('\n*** CPU Architecture not defined. Please use `--arch [x86 | x86_64]`\n')
        sys.exit(2)    
    if not os.path.isdir(root):
        sys.stderr.write('Root dir not found, creating %s\n' % root)
        os.makedirs(root)
    if not os.path.isdir(config):
        sys.stderr.write('creating %s\n' % config)
        os.makedirs(config)
    if not os.path.isfile(installed_db):
        sys.stderr.write('creating %s\n' % installed_db)
        global installed
        installed = {0:{}}
        write_installed()
    if not os.path.isfile(setup_ini):
        sys.stderr.write('getting %s\n' % setup_ini)
        update()
    print '''
    Osgeo4w folders and setup config exist; skeleton environment is complete.

    You might try `apt available` and `apt install` next.
    '''
</t>
<t tx="maphew.20100223163802.3733">def update():
    '''Fetch updated package list from mirror.

        apt update

    Specify mirror (web server, windows file share, local disk):

        apt --mirror=http://example.com/...  update
        apt --mirror=file:////server/share/...  update
        apt --mirror=file://D:/downloads/cache/...  update
    '''
    if not os.path.exists(downloads):
        os.makedirs(downloads)

    # AMR66: bits now is an option
    # bits = 'x86'
    # bits = 'x86_64'
    ##print 'CPU Architecture:', bits

    if not command == 'setup':
        bits = get_setup_arch(setup_ini)
    
    # AMR66: changed to uncompressed ini
    filename =  '%s/%s'%(bits, 'setup.ini')
    source = '%s/%s' % (mirror, filename)
    archive = os.path.join(downloads, filename)

    # backup cached ini archive
    if os.path.exists(archive):
        shutil.copy(archive, archive + '.bak')

    print('Fetching %s' % source)
    dodo_download(source, archive)
##    print('')
##
##    try:
##        uncompressedData = bz2.BZ2File(archive).read()
##    except:
##       raise IOError('\n*** Error decompressing: %s' % archive)
##
    # backup existing setup config
    if os.path.exists(setup_ini):
        shutil.copy(setup_ini, setup_bak)

    shutil.copy(archive, setup_ini)
##
##    # save uncompressed ini to setup dir
##    ini = open(setup_ini, 'w')
##    ini.write(uncompressedData)
##    ini.close

    save_config('last-mirror', mirror)
</t>
<t tx="maphew.20100223163802.3764">def write_installed ():
    ''' Record installed packages in install.db '''
    file = open (installed_db, 'w')
    file.write (installed_db_magic)
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise TypeError('urg')
</t>
<t tx="maphew.20140920000632.1627">By convention, a Startup node contains settings, scripts, etc.
that mostly one wants to have hidden.
</t>
<t tx="maphew.20140920000632.1628">@language python
import os
trace = True
g.cls()
c.setComplexCommand('make-sphinx')
c.save()
aList = c.rstCommands.rst3()
if aList:
    path = g.os_path_finalize_join(g.app.loadDir,'..','doc','html')
    os.chdir(path)
    if len(aList) &gt; 1: g.execute_shell_commands('make clean',trace=trace)
    g.execute_shell_commands('make html',trace=trace)
    fn = aList[0].h.strip() if len(aList) == 1 else 'leo_toc.html'
    fn = g.os_path_finalize_join(path,'_build','html',g.os_path_basename(fn))
    if g.os_path_exists(fn):
        # Don't wait for this command to exit!
        g.execute_shell_commands(['&amp;%s' % (fn)],trace=trace)
</t>
<t tx="maphew.20140920000632.1629">**Imortant**: to take effect, all settings must be descendants of this
@settings node.

**Note**: This file colors text as reStructuredText by default because of
the setting::

    @string target_language = rest
</t>
<t tx="maphew.20140920000632.1630">The default language if no @language or @comment is in effect.

Valid values are (case is ignored):

actionscript,c,csharp,css,cweb,elisp,html,java,latex,
pascal,perl,perlpod,php,plain,plsql,python,rapidq,rebol,shell,tcltk.</t>
<t tx="maphew.20140920000632.1631"></t>
<t tx="maphew.20140920000632.1632"># Use False when using Sphinx</t>
<t tx="maphew.20140920000632.1633"></t>
<t tx="maphew.20140920000632.1634"></t>
<t tx="maphew.20140920000632.1691"></t>
<t tx="maphew.20140922213912.1720">@language python</t>
<t tx="maphew.20140922213912.1721"></t>
<t tx="maphew.20140927120559.1738">@language python
</t>
<t tx="maphew.20140927121126.1789">''' Sample of installed.db.

    package_name    archive_filename    [?]  
'''
@killcolor

INSTALLED.DB 2
libxml2 libxml2-2.9.1-1.tar.bz2 0
gdal110dll gdal110dll-1.10.1-1.tar.bz2 0
libtiff libtiff-4.0.2-2.tar.bz2 0
libjpeg12 libjpeg12-6b-3.tar.bz2 0
python-core python-core-2.7.4-3.tar.bz2 0
netcdf netcdf-3.6.1-1.tar.bz2 0
freexl freexl-1.0.0e-1.tar.bz2 0
curl curl-7.15.1-2.tar.bz2 0
msvcrt msvcrt-1.0.1-12.tar.bz2 0
iconv iconv-1.9.1-1.tar.bz2 0
sip sip-4.12.1-4.tar.bz2 0
libpq libpq-8.3.10-3.tar.bz2 0
geos geos-3.4.2-1.tar.bz2 0
libintl libintl-0.14.4-2.tar.bz2 0
spatialite spatialite-4.1.1-1.tar.bz2 0
spatialite3dll spatialite-3.0.1-0.tar.bz2 0
libmysql libmysql-5.0.18-1.tar.bz2 0
sqlite3 sqlite3-3.7.17-1.tar.bz2 0
python-help python-help-2.7.4-1.tar.bz2 0
proj proj-4.8.0-0.tar.bz2 0
shell shell-1.0.0-13.tar.bz2 0
python python-2.7.4-2.tar.bz2 0
xerces-c xerces-c-2.7.0-1.tar.bz2 0
qt4-libs qt4-libs-4.7.1-6.tar.bz2 0
pyqt4 pyqt4-4.8.3-2.tar.bz2 0
proj-hpgn proj-hpgn-1.0-1.tar.bz2 0
python-tools python-tools-2.7.4-1.tar.bz2 0
gdal19dll gdal19dll-1.9.2-1.tar.bz2 0
openjpeg openjpeg-2.0.0-1.tar.bz2 0
gdal gdal-1.11.0-2.tar.bz2 0
msys msys-1.0.18-7.tar.bz2 0
xerces-c-vc9 xerces-c-vc9-3.1.1-2.tar.bz2 0
gdal18dll gdal-1.8.1-0.tar.bz2 0
ogdi ogdi-3.2.0b1-4.tar.bz2 0
python-testsuite python-testsuite-2.7.4-1.tar.bz2 0
hdf4 hdf4-4.2.0r3-4.tar.bz2 0
hdf5 hdf5-1.8.11-1.tar.bz2 0
libjpeg libjpeg-6b-5.tar.bz2 0
proj-datumgrid proj-datumgrid-1.5-1.tar.bz2 0
setup setup-1.0.7-10.tar.bz2 0
zlib zlib-1.2.3-1.tar.bz2 0
gdal15dll gdal-1.5.4-1.tar.bz2 0
szip szip-2.1-1.tar.bz2 0
python-tcltk python-tcltk-2.7.4-1.tar.bz2 0
openssl openssl-1.0.1g-1.tar.bz2 0
libgeotiff libgeotiff-1.3.0-3.tar.bz2 0
expat expat-2.0.1-1.tar.bz2 0
</t>
<t tx="maphew.20170329101849.1"></t>
<t tx="maphew.20170329101925.1"></t>
<t tx="maphew.20170329101925.10">def write_installed ():
    ''' Record installed packages in install.db '''
    file = open (installed_db, 'w')
    file.write (installed_db_magic)
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise TypeError('urg')
</t>
<t tx="maphew.20170329101925.2">(uncached) maphew.20100223163802.3732
Diff...
- def setup(target):
?           ------
+ def setup ():
?          +
+     '''skeleton installed packages environment'''
-     '''Create skeleton Osgeo4W folders and setup database environment'''
-     if not bits:
-         sys.stderr.write('\n*** CPU Architecture not defined. Please use `--arch [x86 | x86_64]`\n')
-         sys.exit(2)    
-     if not os.path.isdir(root):
+     if not os.path.isdir (root):
?                         +
-         sys.stderr.write('Root dir not found, creating %s\n' % root)
+         sys.stderr.write ('Root dir not found, creating %s\n' % root)
?                         +
-         os.makedirs(root)
+         os.makedirs (root)
?                    +
-     if not os.path.isdir(config):
+     if not os.path.isdir (config):
?                         +
-         sys.stderr.write('creating %s\n' % config)
+         sys.stderr.write ('creating %s\n' % config)
?                         +
-         os.makedirs(config)
+         os.makedirs (config)
?                    +
-     if not os.path.isfile(installed_db):
+     if not os.path.isfile (installed_db):
?                          +
-         sys.stderr.write('creating %s\n' % installed_db)
+         sys.stderr.write ('creating %s\n' % installed_db)
?                         +
          global installed
          installed = {0:{}}
-         write_installed()
+         write_installed ()
?                        +
-     if not os.path.isfile(setup_ini):
+     if not os.path.isfile (setup_ini):
?                          +
-         sys.stderr.write('getting %s\n' % setup_ini)
+         sys.stderr.write ('getting %s\n' % setup_ini)
?                         +
-         update()
+         update ()
?               +
-     print '''
-     Osgeo4w folders and setup config exist; skeleton environment is complete.
  
-     You might try `apt available` and `apt install` next.
-     '''
</t>
<t tx="maphew.20170329101925.3">def setup ():
    '''skeleton installed packages environment'''
    if not os.path.isdir (root):
        sys.stderr.write ('Root dir not found, creating %s\n' % root)
        os.makedirs (root)
    if not os.path.isdir (config):
        sys.stderr.write ('creating %s\n' % config)
        os.makedirs (config)
    if not os.path.isfile (installed_db):
        sys.stderr.write ('creating %s\n' % installed_db)
        global installed
        installed = {0:{}}
        write_installed ()
    if not os.path.isfile (setup_ini):
        sys.stderr.write ('getting %s\n' % setup_ini)
        update ()

</t>
<t tx="maphew.20170329101925.4">def setup(target):
    '''Create skeleton Osgeo4W folders and setup database environment'''
    if not bits:
        sys.stderr.write('\n*** CPU Architecture not defined. Please use `--arch [x86 | x86_64]`\n')
        sys.exit(2)    
    if not os.path.isdir(root):
        sys.stderr.write('Root dir not found, creating %s\n' % root)
        os.makedirs(root)
    if not os.path.isdir(config):
        sys.stderr.write('creating %s\n' % config)
        os.makedirs(config)
    if not os.path.isfile(installed_db):
        sys.stderr.write('creating %s\n' % installed_db)
        global installed
        installed = {0:{}}
        write_installed()
    if not os.path.isfile(setup_ini):
        sys.stderr.write('getting %s\n' % setup_ini)
        update()
    print '''
    Osgeo4w folders and setup config exist; skeleton environment is complete.

    You might try `apt available` and `apt install` next.
    '''
</t>
<t tx="maphew.20170329101925.5">(uncached) maphew.20100223163802.3733
Diff...
- def update():
+ def update ():
?           +
-     '''Fetch updated package list from mirror.
+     '''setup.ini'''
+     if not os.path.exists (downloads):
+         os.makedirs (downloads)
  
-         apt update
+     source = mirror + '/setup.ini.bz2'
+     archive = downloads + 'setup.ini.bz2'
  
-     Specify mirror (web server, windows file share, local disk):
+     # backup existing setup config
+     if os.path.exists (setup_ini):
+         if os.path.exists (setup_bak):
+                 os.remove (setup_bak)
+         os.rename (setup_ini, setup_bak)
  
+    # remove cached ini
+     if os.path.exists (archive):
+         os.remove (archive)
-         apt --mirror=http://example.com/...  update
-         apt --mirror=file:////server/share/...  update
-         apt --mirror=file://D:/downloads/cache/...  update
-     '''
-     if not os.path.exists(downloads):
-         os.makedirs(downloads)
  
+    # get current ini
+     f = urllib.urlretrieve(source, archive, down_stat)
+     uncompressedData = bz2.BZ2File(archive).read()
-     # AMR66: bits now is an option
-     # bits = 'x86'
-     # bits = 'x86_64'
-     ##print 'CPU Architecture:', bits
  
+     # save uncompressed ini to setup dir
+     ini = open(setup_ini, 'w')
+     ini.write(uncompressedData)
+     ini.close
-     if not command == 'setup':
-         bits = get_setup_arch(setup_ini)
-     
-     # AMR66: changed to uncompressed ini
-     filename =  '%s/%s'%(bits, 'setup.ini')
-     source = '%s/%s' % (mirror, filename)
-     archive = os.path.join(downloads, filename)
  
-     # backup cached ini archive
-     if os.path.exists(archive):
-         shutil.copy(archive, archive + '.bak')
- 
-     print('Fetching %s' % source)
-     dodo_download(source, archive)
- ##    print('')
- ##
- ##    try:
- ##        uncompressedData = bz2.BZ2File(archive).read()
- ##    except:
- ##       raise IOError('\n*** Error decompressing: %s' % archive)
- ##
-     # backup existing setup config
-     if os.path.exists(setup_ini):
-         shutil.copy(setup_ini, setup_bak)
- 
-     shutil.copy(archive, setup_ini)
- ##
- ##    # save uncompressed ini to setup dir
- ##    ini = open(setup_ini, 'w')
- ##    ini.write(uncompressedData)
- ##    ini.close
- 
-     save_config('last-mirror', mirror)
</t>
<t tx="maphew.20170329101925.6">def update ():
    '''setup.ini'''
    if not os.path.exists (downloads):
        os.makedirs (downloads)

    source = mirror + '/setup.ini.bz2'
    archive = downloads + 'setup.ini.bz2'

    # backup existing setup config
    if os.path.exists (setup_ini):
        if os.path.exists (setup_bak):
                os.remove (setup_bak)
        os.rename (setup_ini, setup_bak)

   # remove cached ini
    if os.path.exists (archive):
        os.remove (archive)

   # get current ini
    f = urllib.urlretrieve(source, archive, down_stat)
    uncompressedData = bz2.BZ2File(archive).read()

    # save uncompressed ini to setup dir
    ini = open(setup_ini, 'w')
    ini.write(uncompressedData)
    ini.close

</t>
<t tx="maphew.20170329101925.7">def update():
    '''Fetch updated package list from mirror.

        apt update

    Specify mirror (web server, windows file share, local disk):

        apt --mirror=http://example.com/...  update
        apt --mirror=file:////server/share/...  update
        apt --mirror=file://D:/downloads/cache/...  update
    '''
    if not os.path.exists(downloads):
        os.makedirs(downloads)

    # AMR66: bits now is an option
    # bits = 'x86'
    # bits = 'x86_64'
    ##print 'CPU Architecture:', bits

    if not command == 'setup':
        bits = get_setup_arch(setup_ini)
    
    # AMR66: changed to uncompressed ini
    filename =  '%s/%s'%(bits, 'setup.ini')
    source = '%s/%s' % (mirror, filename)
    archive = os.path.join(downloads, filename)

    # backup cached ini archive
    if os.path.exists(archive):
        shutil.copy(archive, archive + '.bak')

    print('Fetching %s' % source)
    dodo_download(source, archive)
##    print('')
##
##    try:
##        uncompressedData = bz2.BZ2File(archive).read()
##    except:
##       raise IOError('\n*** Error decompressing: %s' % archive)
##
    # backup existing setup config
    if os.path.exists(setup_ini):
        shutil.copy(setup_ini, setup_bak)

    shutil.copy(archive, setup_ini)
##
##    # save uncompressed ini to setup dir
##    ini = open(setup_ini, 'w')
##    ini.write(uncompressedData)
##    ini.close

    save_config('last-mirror', mirror)
</t>
<t tx="maphew.20170329101925.8">(uncached) maphew.20100223163802.3764
Diff...
  def write_installed ():
-     ''' Record installed packages in install.db '''
?                ----------       -
+     # ''' Record package in install.db '''
?    ++
      file = open (installed_db, 'w')
      file.write (installed_db_magic)
      file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                    installed[0].keys ()))
      if file.close ():
-         raise TypeError('urg')
?               ----------     -
+         raise 'urg'
+ 
</t>
<t tx="maphew.20170329101925.9">def write_installed ():
    # ''' Record package in install.db '''
    file = open (installed_db, 'w')
    file.write (installed_db_magic)
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise 'urg'

</t>
</tnodes>
</leo_file>
