Apt
===

*[will be] an in-depth exploration of what Apt does and how it gets there.*

What does apt do? In essence:

(A) Install applications:  
Download a package from the mirror,  
unpack it under OSGEO4W_ROOT,  
run any post-install scripts,  
update installed applications list,  
save metadata (cache folder, mirror list).

(B) Show information about A.

(C) Remove installed packages.


### Other docs ###

 - [Introduction](Readme.md) and daily use
 - [Release Notes](Release_notes.md)
 - [Coding conventions](Conventions.md)


Structure
---------

`etc/setup` is the core data library. 

### installed.db ###

list of installed packages, and the archive they were installed from. Space delimited, `packagename archive_filename {unknown}`

    INSTALLED.DB 2
    gs gs-9.07-3.tar.bz2 0
    gdal110dll gdal110dll-1.10.1-1.tar.bz2 0
    python-qscintilla python-qscintilla-2.6.2-2.tar.bz2 0


### Setup.rc ###
 
Setup.exe resource file, for remembering download mirror, local folder for storing cache files. etc. 

    last-cache
    	B:/Osgeo4w/var/cache/setup
    last-mirror
    	http://download.osgeo.org/osgeo4w/


### *.lst.gz ###

What files were installed from the package, relative to OSGEO4W_ROOT. Used to feed program removal function.

    OSGeo4W.bat
    OSGeo4W.ico
    bin
    bin/o-help.bat
    etc
    etc/postinstall
    etc/preremove
    etc/preremove/shell.bat
    etc/postinstall/shell.bat.done
    C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OSGeo4W\OSGeo4W.lnk
    C:\ProgramData\Desktop\OSGeo4W.lnk


### Setup.ini ###

The main library file listing available application names, descriptions, category, required applications, version, etc. It is a local copy of what is available on the configured mirror server (Setup.ini.bz2). 
 

Header metadata:

    arch: x86
    setup-timestamp: 1422778027

An application record:

    @ gdal
    sdesc: "The GDAL/OGR library and commandline tools"
    ldesc: "The GDAL/OGR library and commandline tools"
    category: Libs Commandline_Utilities
    requires: shell libpng libtiff libjpeg libgeotiff proj curl geos libmysql sqlite3 netcdf libpq expat xerces-c-vc9 hdf4 hdf5 ogdi iconv openjpeg spatialite freexl gdal15dll gdal18dll gdal19dll gdal110dll
    version: 1.11.1-5
    install: x86/release/gdal/gdal-1.11.1-5.tar.bz2 5429868 d353f0b89e4be8f1e7312875cb847d2f
    source: x86/release/gdal/gdal-1.11.1-5-src.tar.bz2 5867 c7ac53c38eda4dd88c59a448970e10bc
    [prev]
    version: 1.11.1-4
    install: x86/release/gdal/gdal-1.11.1-4.tar.bz2 5430991 3b60f036f0d29c401d0927a9ae000f0c
    source: x86/release/gdal/gdal-1.11.1-4-src.tar.bz2 4542 d059be7ee572e24cca733870871f32dc

See OSGeo4W [packaging instructions](https://trac.osgeo.org/osgeo4w/wiki/PackagingInstructions) for how these records are generated.


At runtime Apt parses setup.ini into a nested dictionary and uses it like this snippet from `get_info()` (in user-land: *`apt info shell`*):

    pkg_info = get_info(pkg)
    for key in ['name', 'version', zip_path']:
        print('{0:9}: {1}'.format(key, pkg_info[key]))

emits:

    name     : shell
    version  : 1.0.0-13
    zip_path : x86/release/shell/shell-1.0.0-13.tar.bz2

*MISSING: above is an example of using inner-most dict. Need to add description and use of the other layers.*

Resources
---------------

 - https://trac.osgeo.org/osgeo4w/wiki/PackagingInstructions
 - https://trac.osgeo.org/osgeo4w/wiki/SetupDevelopment
 - http://cygwin.com/setup.html

