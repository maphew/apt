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


Apt Structure
-------------
### Globals ###

**`installed`** - in memory dictionary of *installed.db*, created by `get_installed()`

    {status_int : {pkg_name : archive_name}}



Osgeo4W Structure
-----------------

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

## dev environment c.2022
_DRAFT. This project has been starred a couple of times recently, so I figured it's worth doing a bit of work to figure out how much of it still relevant/useful. ;-)_

~~~
conda create -n apt27 python=2.7
conda activate apt27
pip install -r requirements.txt
~~~

Testing setup:
~~~
python .\apt.py --root=c:\temp\apt --bits=64 setup
python .\apt.py --root=c:\temp\apt --bits=64 install iconv
~~~

~~~
PKGS: Checking install status: iconv

Requirement         Installed   (Available)
-------------------------------------------
msvcrt2008          -           (1.0.0-1)
msvcrt2010          -           (1.0.0-2)
msvcrt              -           (1.0.3-1)
setup               -           (1.0.7-16)
shell               -           (1.0.2-4)
iconv               -           (1.14-1)

REQS: --- To install: msvcrt2008 msvcrt2010 msvcrt setup shell iconv

Preparing to download: msvcrt2008
[==================================================] 100% 4,968,079
Saved C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\msvcrt\msvcrt2008\msvcrt2008-1.0.0-1.tar.bz2   

msvcrt2008 = C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\msvcrt\msvcrt2008\msvcrt2008-1.0.0-1.tar.bz2
--- Verifying local file's md5 hash matches mirror
        True
        remote: 432ad651a1c401513912749cc90dca66
        local:  432ad651a1c401513912749cc90dca66

CMD c:\temp\apt
» for %f in ("C:\Users\Matt\AppData\Local\Temp") do call set TEMPDRIVE=%~df 

CMD c:\temp\apt
» call set TEMPDRIVE=C: 

CMD c:\temp\apt
» cd C:\Users\Matt\AppData\Local\Temp 

CMD C:\Users\Matt\AppData\Local\Temp
» "c:\temp\apt\bin\vcredist-2008-sp1-x64.exe" /q 
~~~

Can appear frozen at this point. Look for UAC popup asking for permissions to continue install.

~~~
CMD C:\Users\Matt\AppData\Local\Temp
» if errorlevel 3010 echo1>"c:\temp\apt\etc\reboot" 

CMD C:\Users\Matt\AppData\Local\Temp
» del "c:\temp\apt\bin\vcredist-2008-sp1-x64.exe" 
Post_install complete, return code 0
Preparing to download: msvcrt2010
[==================================================] 100% 5,683,309
Saved C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\msvcrt\msvcrt2010\msvcrt2010-1.0.0-2.tar.bz2   

msvcrt2010 = C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\msvcrt\msvcrt2010\msvcrt2010-1.0.0-2.tar.bz2
--- Verifying local file's md5 hash matches mirror
        True
        remote: 4909547dec4eb6db922912858b5802a5
        local:  4909547dec4eb6db922912858b5802a5

CMD c:\temp\apt
» for %f in ("C:\Users\Matt\AppData\Local\Temp") do call set TEMPDRIVE=%~df 

CMD c:\temp\apt
» call set TEMPDRIVE=C: 

CMD c:\temp\apt
» cd C:\Users\Matt\AppData\Local\Temp 

CMD C:\Users\Matt\AppData\Local\Temp
» "c:\temp\apt\bin\vcredist-2010-x64.exe" /q /norestart 

CMD C:\Users\Matt\AppData\Local\Temp
» if errorlevel 3010 echo1>"c:\temp\apt\etc\reboot" 

CMD C:\Users\Matt\AppData\Local\Temp
» del "c:\temp\apt\bin\vcredist-2010-x64.exe" 
Post_install complete, return code 0
Preparing to download: msvcrt
[==================================================] 100% 792,156
Saved C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\msvcrt\msvcrt-1.0.3-1.tar.bz2

msvcrt = C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\msvcrt\msvcrt-1.0.3-1.tar.bz2
--- Verifying local file's md5 hash matches mirror
        remote: 55a5b8b9a4204eefbc8eae075bd4a78f
        local:  55a5b8b9a4204eefbc8eae075bd4a78f
Preparing to download: setup
[==================================================] 100% 393,958
Saved C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\setup\setup-1.0.7-16.tar.bz2

setup = C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\setup\setup-1.0.7-16.tar.bz2
--- Verifying local file's md5 hash matches mirror
        True
        remote: dd8477c124d48144c2671e1aca766f5c
        local:  dd8477c124d48144c2671e1aca766f5c

CMD c:\temp\apt
» nircmd shortcut "c:\temp\apt\bin\nircmd.exe" "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OSGeo4W" "Setup" "exec hide ~qc:\temp\apt\bin\setup.bat~q" "c:\temp\apt\OSGeo4W.ico"

CMD c:\temp\apt
» textreplace -std -t bin/setup.bat 

CMD c:\temp\apt
» textreplace -std -t bin/setup-test.bat 
Post_install complete, return code 0
Preparing to download: shell
[==================================================] 100% 3,011
Saved C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\shell\shell-1.0.2-4.tar.bz2

shell = C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\shell\shell-1.0.2-4.tar.bz2
--- Verifying local file's md5 hash matches mirror
        True
        remote: 5b42d3e5c946bccaa1313ee768fd5694
        local:  5b42d3e5c946bccaa1313ee768fd5694
mkdir was unexpected at this time.

CMD c:\temp\apt
» if not ==0 mkdir "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OSGeo4W"
Post_install complete, return code 255
Preparing to download: iconv
[==================================================] 100% 704,559
Saved C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\iconv\iconv-1.14-1.tar.bz2

iconv = C:\Users\Public\Downloads\http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f\x86_64\release\iconv\iconv-1.14-1.tar.bz2
--- Verifying local file's md5 hash matches mirror
        True
        remote: d5e71014388f54f131bf197d50740f96
        local:  d5e71014388f54f131bf197d50740f96

(apt) PS C:\Users\Matt\code\apt> 
~~~

Wow. It still works, mostly. :)
Start menu items don't seem to be there, but manually running running `c:\temp\apt\Osgeo4W.bat` yields:

```
o-help for a list of available commands
CMD C:\temp\apt
» o-help
                   -={ OSGeo4W Shell Commands }=-
  dllupdate                               nircmd
  nircmdc                                 osgeo4w-setup
  textreplace                             xxmklink
  o-help                                  o4w_env
  setup-test                              setup

CMD C:\temp\apt
»
```
