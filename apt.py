#!/usr/bin/env python
#@+leo-ver=5-thin
#@+node:maphew.20150327024628.2: * @file apt.py
#@@first
#@@language python
#@@tabwidth -4
#@+<<docstring>>
#@+node:maphew.20100307230644.3846: ** <<docstring>>
'''Apt command line installer and package manager for Osgeo4W.

Examples
--------
Typical daily use::

    apt update                   (fetch up-to-date setup.ini)
    apt install gdal gdal-python (install packages "gdal" and "gdal-python", and dependencies)
    apt new                      (show possible upgrades)
    apt list                     (show installed packages)
    apt available                (show installation candidates)
    apt remove xxx yyy           (uninstall packages xxx and yyy)

Notes
-----
Apt strives to match Osgeo4wSetup.exe's results as closely as possible, and uses
the same configuration and install manifest files. A prime directive is that
user's should never be put in a position where they feel the need to choose
between the tools and not go back.

That's the aspiration. There's no guarantee it's been achieved.

At the moment apt can only install the 32bit Osgeo4W packages.

References
----------
.. [1] Based on ``cyg-apt`` - "Cygwin installer to keep cygwin root up to date"
    (c) 2002--2003  Jan Nieuwenhuizen <janneke@gnu.org>
    License: GNU GPL

    Modified by Matt.Wilkie@gov.yk.ca for OSGeo4W,
    beginning July 2008
'''
apt_version = '0.4'
#@-<<docstring>>
#@+<<imports>>
#@+node:maphew.20100307230644.3847: ** <<imports>>
import __main__
import getopt
import os
import glob
import re
import shutil
import string
import sys
import urllib
import gzip, tarfile, bz2
import hashlib
import requests
import subprocess
import shlex
import stat
import locale
import knownpaths # for fetching Windows special folders
from pkg_resources import parse_version # for version comparing
from datetime import datetime, timedelta
#from attrdict import AttrDict

#@-<<imports>>
#@@language python
#@@tabwidth -4
#@+others
#@+node:maphew.20100223163802.3718: ** usage
def usage ():
    print('-={ %s }=-\n'% apt_version)
      # better:  use parsopt instead, #53 http://trac.osgeo.org/osgeo4w/ticket/53
    sys.stdout.write ('''apt [OPTION]... COMMAND [PACKAGE]...

Commands:
    available -  show packages available to be installed
    ball - print full path name of package archive
    download - download package
    find - package containing file (from installed packages)
    hashcheck - check md5 sum of local package vs mirror
    help - show help for COMMAND
    info - report name, version, category etc. for specified packages
    install - download and install packages, including dependencies
    list - report installed packages
    listfiles - installed with package X
    missing - print missing dependencies for X
    new - list available upgrades to currently installed packages
    remove - uninstall packages
    requires - report package dependencies
    search - search available packages list for X
    setup - skeleton installed packages environment
    update - setup.ini
    upgrade - all installed packages
    url - print package archive path, relative to mirror root
    version - print installed version of X

Options:
    -b,--bits=32/64        use 32 or 64bit package mirror (only used with `apt setup`)
    -d,--download          download only
    -i,--ini=FILE          use setup.ini [%(setup_ini)s]
    -m,--mirror=URL        use mirror [%(mirror)s]
    -r,--root=DIR          set osgeo4w root [%(root)s]
    -t,--t=NAME            set dist name (*curr*, test, prev)
    -x,--no-deps           ignore dependencies
    -s,--start-menu=NAME   set the start menu name (OSGeo4W)
       --debug             display debugging statements
''' % {'setup_ini':setup_ini,'mirror':mirror,'root':root}) #As they were just printing as "%(setup_ini)s" etc...
#@+node:maphew.20121113004545.1577: ** check_env
def check_env(o4w=''):
    '''Verify we're running in an Osgeo4W-ready shell'''
    #From command line:
    if o4w:
        OSGEO4W_ROOT = o4w
        os.environ['OSGEO4W_ROOT'] = o4w
        os.environ['OSGEO4W_ROOT_MSYS'] = OSGEO4W_ROOT # textreplace.exe needs this (post_install)
        OSGEO4W_ROOT = OSGEO4W_ROOT.replace('\\', '/')
    #From environment:
    elif 'OSGEO4W_ROOT' in os.environ.keys():
        OSGEO4W_ROOT = os.environ['OSGEO4W_ROOT']
        os.putenv('OSGEO4W_ROOT_MSYS', OSGEO4W_ROOT)
        OSGEO4W_ROOT = string.replace(OSGEO4W_ROOT, '\\', '/')
    else:
       sys.stderr.write('error: Please set OSGEO4W_ROOT or use --root=DIR\n')
       sys.exit(2)

    return OSGEO4W_ROOT
#@+node:maphew.20121111221942.1497: ** check_setup
def check_setup(installed_db, setup_ini):
    '''Look to see if the installed packages db and setup.ini are available'''
##    for i in (installed_db, setup_ini):
##        if not os.path.isfile(i):
##            sys.stderr.write('error: %s no such file\n' % i)
##            sys.stderr.write('error: set OSGEO4W_ROOT and run "apt setup"\n')
##            sys.exit(2)
    # AMR66: above changed, because not compatible with osgeo-setup
    failed = ""
    if not os.path.isfile(installed_db):
        failed = installed_db

    # search for setup.ini:
    if not os.path.isfile(setup_ini):
        filename =  '%s/%s'%(bits, 'setup.ini')
        archive = os.path.join(downloads, filename)
        # copy it, like update() does
        if os.path.isfile(archive):
            shutil.copy(archive, setup_ini)
        else:
            failed = archive

    if failed:
        sys.stderr.write('error: %s no such file\n' % failed)
        sys.stderr.write('error: set OSGEO4W_ROOT and run "apt setup"\n')
        sys.exit(2)

#@+node:maphew.20100302221232.1487: ** Commands
#@+node:maphew.20100223163802.3719: *3* available
def available(dummy):
    '''Show packages available on the mirror.

    Display packages available on the mirror, with installed packages marked ``*``.
    Specify an alternate mirror with ``--mirror=...``

    Parameters
    ----------
    dummy : str
        Parameter is not used at present.

    Returns
    -------
    list
        Package names (without install mark).
    '''
    # All packages mentioned in setup.ini for the specified distribution
    a_list = dists[distname].keys()

    # mark installed packages
    i_list = list(a_list)
    for p in installed[0].keys():
        i_list.remove(p)
        i_list.append('%s*' % p)

    # Report to user, in columns, courtesy of Aaron Digulla,
    # http://stackoverflow.com/questions/1524126/how-to-print-a-list-more-nicely
    print '\n {} Packages available to install (* = already installed)\n'.format(len(i_list))
    i_list.sort()
    split = len(i_list)/2
    col1 = i_list[0:split]
    col2 = i_list[split:]
    for key, value in zip(col1,col2):
        print '{:<30}{}'.format(key, value)

    return a_list
#@+node:maphew.20100223163802.3720: *3* ball
def ball(packages):
    '''Print full local path name of package archive

    C:\> apt ball shell

    shell = d:/temp/o4w-cache/setup/http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f/x86
/release/shell/shell-1.0.0-13.tar.bz2

    FIXME: This should either return a list of archive filenames,
    or there should be a get_ball(p) which returns 1 filename,
    or we should rip out all this repetitive code spread across multiple functions,
    for the purpose of allowing multiple package input. We need a handler for this instead.
    '''
    if isinstance(packages, basestring): packages = [packages]

    if not packages:
        help('ball')
        sys.stderr.write("\n*** No package names specified. ***\n")
        return

    for p in packages:
        d = get_info(p)
        print "\n%s = %s" % (p, d['local_zip'])
    
    return
#@+node:maphew.20100223163802.3721: *3* download
def download(packages):
    '''Download the package(s) from mirror and save in local cache folder:

    C:\> apt download shell gdal {...etc}

    shell = d:/temp/o4w-cache/setup/http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f/x86/release/shell/shell-1.0.0-13.tar.bz2
    remote:  c38f03d2b7160f891fc36ec776ca4685  shell-1.0.0-13.tar.bz2
    local:   c38f03d2b7160f891fc36ec776ca4685  shell-1.0.0-13.tar.bz2

    gdal = d:/temp/o4w-cache/setup/http%3a%2f%2fdownload.osgeo.org%2fosgeo4w%2f/x86/release/gdal/gdal-1.11.1-4.tar.bz2
    remote:  3b60f036f0d29c401d0927a9ae000f0c  gdal-1.11.1-4.tar.bz2
    local:   3b60f036f0d29c401d0927a9ae000f0c  gdal-1.11.1-4.tar.bz2

    Use `apt available` to see what is on the mirror for downloading.
    '''
    if isinstance(packages, basestring): packages = [packages]

    if debug:
        print '\n### DEBUG: %s ###' % sys._getframe().f_code.co_name

    if not packages:
        help('download')
        sys.stderr.write("\n*** No package names specified. ***\n")
        return

    print "Preparing to download:", ', '.join(packages)
    for p in packages:
        do_download(p)
        ball(p)
        hashcheck(p)
#@+node:maphew.20141101125304.3: *3* info
def info(packages):
    '''info - report name, version, category, etc. about the package(s)

    B:\> apt info shell

    name     : shell
    version  : 1.0.0-13
    sdesc    : "OSGeo4W Command Shell"
    ldesc    : "Menu and Desktop icon launch OSGeo4W command shell"
    category : Commandline_Utilities
    requires : msvcrt setup
    zip_path : x86/release/shell/shell-1.0.0-13.tar.bz2
    zip_size : 3763
    md5      : c38f03d2b7160f891fc36ec776ca4685
    local_zip: d:/temp/o4w-cache/setup/http%3.../shell-1.0.0-13.tar.bz2
    installed: True
    install_v: 1.0.0-11

    Notes:
        - "local_zip" is best guess based on current mirror. (We don't record which mirror was in use at the time of package install.)
        - "version" is from setup.ini, what is available on the mirror server
        - "install_v" is the version currently installed
    '''
    if isinstance(packages, basestring): packages = [packages]

    if not packages:
        help('info')
        sys.stderr.write("\n*** Can't show info, no package names specified. ***\n")
        return

    for p in packages:
        d = get_info(p)
        print('')
        # WARNING: only prints fields we know about, if something is added
        # upstream we'll miss it here
        fields = ['name',
            'version',
            'sdesc',
            'ldesc',
            'category',
            'requires',
            'zip_path',
            'zip_size',
            'md5',
            'local_zip',
            'installed']
        for k in fields:
            print('{0:9}: {1}'.format(k,d[k]))
        if d['installed']:
            print('{0:9}: {1}'.format('install_v',d['install_v']))

        if debug:
            # This guaranteed to print entire dict contents,
            # but not in a logical order.
            print '\n----- DEBUG: %s -----' % sys._getframe().f_code.co_name
            for k in d.keys():
                print('{0:8}:\t{1}'.format(k,d[k]))
            print '-' * 36
#@+node:maphew.20100223163802.3722: *3* find
def find(patterns):
    '''Search installed packages for filenames matching the specified text string.'''
    if not patterns:
        sys.stderr.write('\nFind what? Enter a filename to look for (partial is ok).\n')
        return

    for p in patterns:
        print '--- %s:' % p
        hits = []
        for package in sorted(installed[0].keys()):
            for line in get_filelist(package):
                if p.lower() in line.lower():
                    hits.append('%s: /%s' % (package, line))
        results = (string.join(hits, '\n'))
        if results:
            print results

    return results
#@+node:maphew.20100223163802.3723: *3* help
def help(*args):
    '''Show help for COMMAND'''
    action = args[-1] # ([],) --> []
    if type(action) is str: action = [action] # convert bare string to list

    # Show general usage help when no specific action named
    if not (action) or (action == ['help']):
        usage()
        sys.exit(0)

    action = action[-1] # ['help','remove'] --> 'remove'

    # display the function's docstring
    d = __main__.__dict__
    if action in d.keys():
        print "\n" + d[action].__doc__
    else:
        print 'Sorry, function "%s" not found in __main__' % action
#@+node:maphew.20100223163802.3724: *3* install
def install(packages, force=False):
    '''Download and install packages, including dependencies

        C:\> apt install shell gdal
    '''
    if isinstance(packages, basestring): packages = [packages]
    # where do we get those...?
    while '' in packages:
        packages.remove('')
        if debug: print "--- Found and removed extraneous '' in `packages`"

    if debug:
        print '\n--- DEBUG: %s ---' % sys._getframe().f_code.co_name
        print '--- pkgs:', packages

    if not packages:
        sys.stderr.write('\n*** No packages specified. Use "apt available" for ideas. ***\n')
        help('install')
        return

    # build list of dependencies
    reqs = []
    reqs = get_all_dependencies(packages, reqs)
    if debug: print 'PKGS: %s, REQS: %s' % (packages, reqs)

    print '\nPKGS: Checking install status: {}\n'.format(' '.join(packages))
    print '{:20}{:12}({})\n{}'.format('Requirement', 'Installed', 'Available', '-'*43)
    delete = []
    for p in reqs:
        p_installed = get_info(p)['installed']
        ini_v = version_to_string(get_version(p))
        print '{:19}'.format(p),
        if p_installed:
            local_v = version_to_string(get_installed_version(p))
            if parse_version(local_v) >= parse_version(ini_v):
                print '{:12}({})'.format(local_v, ini_v)
                delete.append(p)
        else:
            print '{:12}({})'.format('-', ini_v)

    # safety first: delete after loop
    reqs = [x for x in reqs if x not in delete]

    if reqs:
        print '\nREQS: --- To install: {}\n'.format(' '.join(reqs))
        for r in reqs:
            download(r)
            if download_p:  # quit if download only flag is set
                continue
            do_install(r)

    else:
        print '\nPackages and required dependencies are installed.\n'
        version(pkgs_requested)
        print ''
        version(reqs_requested)
#@+node:maphew.20100510140324.2366: *4* install_next (missing_packages)
def install_next(packages, resolved, seen):
##    global packagename
    for p in packages:
        if p in resolved:
            continue
        seen.add(p)
        dependences = get_missing(p)
        dependences.remove(p)
        for dep in dependences:
            if dep in resolved:
                continue
            if dep in seen:
                raise Exception(
                    'Required package %s from %s is a circular reference '
                    'with a previous dependent' % (dep, p))
            install_next(dependences, resolved, seen)

        if installed[0].has_key(p):
            sys.stderr.write('preparing to replace %s %s\n' \
                      % (p, version_to_string(get_installed_version(p))))
            do_uninstall(p)
        sys.stderr.write('installing %s %s\n' \
                  % (p, version_to_string(get_version(p))))
        do_install(p)
        resolved.add(p)
#@+node:maphew.20150208163633.3: *4* def unique
def unique(L):
    '''Remove duplicates and empty items from a list'''
    L = list(set(L))
    L = [i for i in L if i != '']
    return L
#@+node:maphew.20100223163802.3725: *3* list_installed
def list_installed(dummy):
    '''List installed packages'''
    # fixme: once again, 'dummy' defined but not used. fix after calling structure is refactored
    ## global packagename
    s = '%-20s%-15s' % ('Package', 'Version')
    print s
    s = '%-20s%-15s' % ('-'*18, '-'*10)
    print s
    for p in sorted (installed[0].keys()):
        ins = get_installed_version(p)
        new = 0
        if dists[distname].has_key(p) \
           and dists[distname][p].has_key(INSTALL):
            new = get_version(p)
        s = '%-20s%-15s' % (p, version_to_string(ins))
        if new and new != ins:
            s += '(%s)' % version_to_string(new)
        print s
#@+node:mhw.20120404170129.1475: *3* listfiles
def listfiles(packages):
    '''List files installed with package X. Multiple packages can be specified.

        C:\> apt listfiles shell gdal

        ----- shell -----
        OSGeo4W.bat
        OSGeo4W.ico
        bin
        ...etc

        ----- gdal -----
        bin
        bin/gdal111.dll
        bin/gdaladdo.exe
        ...etc
    '''
    if isinstance(packages, basestring): packages = [packages]
    if not packages:
        help('listfiles')
        sys.stderr.write ('\n*** No packages specified. Use "apt list" to see installed packages.***\n')
        return

    for p in packages:
        print "\n----- %s -----" % p
        for i in get_filelist(p):
            print i

#@+node:maphew.20100223163802.3726: *3* md5
def hashcheck(package):
    '''Check if the md5 hash for "package" in local cache matches mirror

            > apt hashcheck shell

        Returns: True or False for md5 match status
                 None when cache file not found

        If passed a list it only processes the first item.
    '''
    if not package:
        sys.stderr.write('Please specify package to calculate md5 hash value for.')
        return

    if not isinstance(package, basestring):
        package = package[0]

    print "--- Verifying local file's md5 hash matches mirror"
    match = False
    p_info = get_info(package)

    try:
        localname = p_info['local_zip']
        localFile = file(localname, 'rb') #we md5 the *file* not the *filename*
        my_md5 = hashlib.md5(localFile.read()).hexdigest()
        their_md5 = p_info['md5']
        if their_md5 == my_md5:
            match = True

    except IOError:
       sys.stderr.write('*** local {}\'s .bz2 not found ***'.format(package))
       return

    print('\t%s' % match)
    print('\tremote: %s' % their_md5)
    print('\tlocal:  %s' % my_md5)

    return match
#@+node:maphew.20100223163802.3727: *3* missing
def missing(dummy):
    '''Display missing dependencies for all installed packages.

        `dummy` parameter is ignored
    '''
    ## installed[0] is a dict of {'pkg-name': 'pkg.tar.bz2'}
    missing = []
    for pkg in installed[0]:
        result = string.join(get_missing(pkg))
        if result and result not in missing:
            missing.append(result)

    print "\nThe following packages have been listed as dependencies but are not installed:\n"
    for m in missing:
        print '\t%s' % m

    return missing
#@+node:maphew.20150110091755.3: *4* get_missing
def get_missing(packagename):
    '''For package, identify any requirements (dependencies) that are not installed.

       Returns a dictionary of {packagname: ['missing_1','missing_2','...']}
    '''
    if debug:
        print '\n### DEBUG: %s ###' % sys._getframe().f_code.co_name

    # build list of required packages
    reqs = get_info(packagename)['requires'].split()

    #depends = get_requires(packagename)
    depends = get_all_dependencies(packagename, [])
        #debug: #21
    # print reqs
    # print depends

    # determine which requires are not installed
    lst = []
    for pkg in reqs:
        if debug: print 'DEBUG: get_info.reqs.pkg:', pkg
        if not pkg in installed[0]:
            lst.append(pkg)

    # if list exists, and packagename isn't in it,
    # something else has listed packagename as a dependency
    # fixme: look back up stream and see who asked for it.
    if lst and packagename not in lst:
        sys.stderr.write('warning: missing package: %s\n' % string.join(lst))

    # I think this is out of place. We've only been asked to identify what's missing,
    # not if there are new versions available; scope creep.
    elif packagename in installed[0]:
        ins = get_installed_version(packagename)
        new = get_version(packagename)
        if ins >= new:
            #sys.stderr.write('%s is already the newest version\n' % packagename)
            #lst.remove(packagename)
            pass
        elif packagename not in lst:
            lst.append(packagename)

    return lst
#@+node:maphew.20100223163802.3728: *3* new
def new(dummy):
    '''List available upgrades to currently installed packages'''

    print '%-20s%-12s%s' % ('Package', 'Installed', 'Available')
    print '%-20s%-12s%s' % ('-'*17, '-'*9, '-'*10)
    for p in sorted(get_new()):
        print '%-20s%-12s(%s)' % (p,
                version_to_string(get_installed_version(p)),
                version_to_string(get_version(p)),
                )

#@+node:maphew.20100223163802.3729: *3* remove
def remove(packages):
    '''Uninstall listed packages'''
    if not packages:
        sys.stderr.write('No packages specified. Run "apt list" to see installed packages')
        return
    #AMR66:
    if isinstance(packages, basestring): packages = [packages]
    #if type(packages) is str: packages = [packages]

    for p in packages:
        print p
        if not installed[0].has_key(p):
            sys.stderr.write ('warning: %s not installed\n' % p)
            continue
        sys.stderr.write('removing %s %s\n' % \
                        (p, version_to_string(get_installed_version(p))))
        do_uninstall(p)

#@+node:maphew.20100223163802.3730: *3* requires
def requires(packages):
    ''' What packages does X rely on?

        Returns dictionary of package names and dependencies.
        Reports sub-dependencies, but they aren't in the dict (yet).
    '''
    if not packages:
        sys.stderr.write('Please specify package names to list dependencies for.')
        return
    if isinstance(packages, basestring): packages = [packages]

    for p in packages:
        print '----- "%s" requires the following directly to work -----' % p
        depends = {p: get_info(p)['requires'].split()}
        if p in depends[p]:
            depends[p].remove(p) # don't need to list self ;-)
        print string.join(depends[p], '\n')

    print '----- Sub dependencies are ----'
    print string.join(get_all_dependencies(packages, []), '\n')

    return depends
#@+node:maphew.20150327024923.2: *3* xrequires
def xrequires(packages):
    ''' https://github.com/maphew/apt/issues/32 '''
    if isinstance(packages, basestring): packages = [packages]

    dlist = []
    dlist = get_all_dependencies(packages, dlist)
    print dlist
#@+node:maphew.20100223163802.3731: *3* search
def search(pattern):
    ''' Search available packages list and descriptions for X

        Returns list of package names
    '''
    global packagename
    packages = []
    keys = []

    #pattern comes in as a list, we need bare string
    pattern = ' '.join(pattern)

    if not pattern:
        help('search') #stub for when help takes a parameter (print a usage message)
        sys.stderr.write("\n*** Missing what to search for ***\n")
        return

    if distname in dists:
        # build list of packagenames
        keys = dists[distname].keys()
    else:
        print '*** this "else:" does not get used???'
        # finally understand some of the intent for this block:
        # if the distribution name is unknown, dig through all
        # dists. Each key should be a package name.
        for i in dists.keys():
            for j in dists[i].keys():
                if not j in keys:
                    keys.append(j)

    #search for the regexp pattern
    for i in keys:
        pi = get_info(i)
        text = '{} {} {}'.format(pi['name'], pi['sdesc'], pi['ldesc'])

        # append pkg name (key) when pattern is found in text
        if not pattern or re.search(pattern, text):
            # Don't understand this if/else at all. It seems to say
            #   "if True: p.append(i); if False p.append(i)"
            if distname in dists:
                if dists[distname][i].has_key(INSTALL):
                    packages.append(i)
            else:
                packages.append(i)

    for packagename in sorted(packages):
        pi = get_info(packagename)
        print '{:>30} - {}'.format(pi['name'], pi['sdesc'])

    return packages
#@+node:maphew.20100223163802.3732: *3* setup
def setup(target):
    '''Create skeleton Osgeo4W folders and setup database environment'''
    if not bits:
        sys.stderr.write('\n*** CPU Architecture not defined. Please use `--bits [32 | 64]`\n')
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
#@+node:maphew.20100223163802.3733: *3* update
def update():
    '''Fetch updated package list from mirror.

        apt update

    Specify mirror (web server, windows file share, local disk):

        apt --mirror=http://example.com/...  update
        apt --mirror=file:////server/share/...  update
        apt --mirror=file://D:/downloads/cache/...  update
    '''
    global bits
    
    if not os.path.exists(downloads):
        os.makedirs(downloads)

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
#@+node:maphew.20100223163802.3734: *3* upgrade
def upgrade(packages):
    '''Upgrade named packages.

        apt upgrade all
        apt upgrade gdal-filegdb qgis-grass-plugin
    '''
    if not packages:
        help('upgrade')
        sys.stderr.write('*** No packages specified. Use `apt new` for ideas.\n')
        return
    if isinstance(packages, basestring): packages = [packages]

    if packages[0] == 'all':
        packages = get_new()

    install(packages)
#@+node:maphew.20100223163802.3735: *3* url
def url(packages):
    '''Print remote package archive path, relative to mirror root'''
    #AMR66:
    if isinstance(packages, basestring): packages = [packages]
    #if type(packages) is str: packages = [packages]

    if not packages:
        help('url')
        sys.stderr.write('No package specified. Try running "apt available"')
        return

    print mirror
    for p in packages:
        d = get_info(p)
        print '\t%s' % d['zip_path']
#@+node:maphew.20100223163802.3736: *3* version
def version(packages):
    '''Report installed version of X'''
    if isinstance(packages, basestring): packages = [packages]

    if not packages:
        help('version')
        sys.stderr.write('No package specified. Try running "apt list"')
        return

    for p in packages:
        #print '%-20s%-12s' % (p, get_info(p)['version'])
            #broken! this reports Setup.ini version!
        print '%-20s%-12s' % (p, version_to_string(get_installed_version(p)))

#@+node:maphew.20100302221232.1485: ** Helpers
#@+node:maphew.20141228100517.4: *3* exceptionHandler
def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    '''Print user friendly error messages normally, full traceback if DEBUG on.
       Adapted from http://stackoverflow.com/questions/27674602/hide-traceback-unless-a-debug-flag-is-set
    '''
    if debug:
        print '\n*** Error:'
        debug_hook(exception_type, exception, traceback)
    else:
        print "\n%s: %s" % (exception_type.__name__, exception)

#@+node:maphew.20141110231213.3: *3* class AttrDict
class xAttrDict(dict):
    '''Access a dictionary by attributes, like using javascript dotted notation.

        dict.mykey  <--- same as --->   dict['mykey']

    From http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
    '''
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
#@+node:maphew.20100223163802.3737: *3* cygpath
def cygpath(path):
    # change dos path to unix style path, plus add cygwin prefix
    # needs some changes to work for osgeo4w
    # adapted from http://cyg-apt.googlecode.com: cygpath()
    path = path.replace("\\", "/")
    if len(path) == 3:
        if path[1] == ":":
            path = "/" + path[0].lower()
    elif len(path) > 1:
        if path[1] == ":":
            path = "/" + path[0].lower() + path[2:]
    return path

#@+node:maphew.20100223163802.3738: *3* debug_old
def debug_old(s):
    # still haven't figured out quite how this is meant to be used
    # uncomment the print statement to display contents of parsed setup.ini
    s
    print s

#@+node:maphew.20150327181149.2: *3* uniq
def uniq(alist):
    ''' Returns a list with unique items (removes duplicates),
        without losing item order.
        From @jamylak, http://stackoverflow.com/a/17016257/14420
    '''
    from collections import OrderedDict
    return list(OrderedDict.fromkeys(alist))
#@+node:maphew.20150329144423.2: *3* url_time_to_datetime
def url_time_to_datetime(s):
    ''' Convert "last-modified" string time from a web server header to a python
        datetime object.

        Assumes the string looks like "Fri, 27 Mar 2015 08:05:42 GMT". There is
        no attempt to use locale or similar, so the function is'nt very robust.
    '''
    return datetime.strptime(s, '%a, %d %b %Y %X %Z')
#@+node:maphew.20150329144423.3: *3* datetime_to_unixtime
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
        # FIXME: According to official docs, this should only be necessary in
        # py2.6 and earlier # yet it fails for me in py2.7.4! Is osgeo4w's python
        # corrupt?

#@+node:maphew.20100308085005.1379: ** Doers
#@+node:maphew.20100223163802.3739: *3* do_download
def do_download(packagename):
    '''Download package from mirror and save in local cache folder.

    Overwrites existing cached version if md5 sum doesn't match expected from setup.ini.

    Returns `path\to\archive.bz2` on success (file downloaded, or file with correct md5 is present),
    and http status code if fails.
    '''
    p_info = get_info(packagename)
    # amr66: error with no install-tag, grass71-devel
    # if not p_info['zip_path']:
    #     print "*** no download path for package", p
    #     return ''

    dstFile = p_info['local_zip']
    srcFile = p_info['mirror_path']
    cacheDir = os.path.dirname(dstFile)

    if os.path.exists(dstFile)and hashcheck(packagename):
        print 'Skipping download of %s, exists in cache' % p_info['filename']
        return

    if debug:
        print 'do_download():'
        print '\tsrcFile:\t', srcFile
        print '\tdstFile:\t', dstFile

    f = dodo_download(srcFile, dstFile)

    return f
#@+node:maphew.20150322125023.13: *4* dodo_download
def dodo_download(url, dstFile):
    ''' Dumbest name for abstracting downloading
        a file to disk with requests module and progress reporting

        Returns `path\to\archive.bz2` on success, http status code if fails.
    '''
    r = requests.head(url)
    if not r.ok:
        print 'Problem getting %s\nServer returned "%s"' % (url, r.status_code)
        return r.status_code

    url_time = url_time_to_datetime(r.headers['last-modified'])
    if os.path.exists(dstFile):
        file_time = datetime.utcfromtimestamp(os.path.getmtime(dstFile))
    else:
        file_time = datetime(1970, 1, 1)
    if debug:
        print '\tServer URL Last-modified:\t', r.headers['last-modified']
        print '\tDT obj URL Last-modified:\t', url_time
        print '\tLocal cache file modified:\t', file_time

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

#@+node:maphew.20100223163802.3742: *4* down_stat
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
#@+node:maphew.20100223163802.3740: *3* do_install
def do_install(packagename):
    ''' Unpack the package in appropriate locations, write file list to installed manifest, run postinstall confguration.'''

    # filename = dists[distname][packagename]['local_zip']
    # filename = get_zipfile(packagename)
    # amr66-patch-1
    try:
        filename = dists[distname][packagename]['local_zip']
        filename = get_zipfile(packagename)
    except KeyError as e:
        print('***', e)

    if not os.path.exists(filename):
        sys.exit('Local archive %s not found' % filename)

    # unpack
    os.chdir (root)
    pipe = tarfile.open(filename,'r')
    lst = pipe.getnames()
    
    #pipe.extractall() # doesn't overwrite read-only files, Issue #59
    # https://stackoverflow.com/questions/7237475/overwrite-existing-read-only-files-when-using-pythons-tarfile
    # https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows/4829285
    # Py docs say `extractall` is preferred over `extract` as it handles
    # more conditions, so at some future point we may want to rework this.
    for f in pipe:
        try:
            pipe.extract(f)
        except IOError as e:
            print 'Handling %s' % e
            os.chmod(f.name, stat.S_IWRITE)
            os.remove(f.name)
            pipe.extract(f)
        finally:
            os.chmod(f.name, f.mode)
    
    pipe.close()
    if pipe.close():
        raise Exception('urg')

   # record list of files installed
    write_filelist(packagename, lst)

    # run post installation scripts
    if os.path.isdir('%s/etc/postinstall' % root):
        post = glob.glob('%s/etc/postinstall/*.bat' % root)
        if post:
            post_install(packagename)

    #update package details in installed.db
    installed[0][packagename] = os.path.basename(filename)
    write_installed()
#@+node:maphew.20100223163802.3741: *3* do_uninstall
def do_uninstall(packagename):
    '''For package X: delete installed files & remove from manifest, remove from installed.db'''
    # TODO: remove empty dirs?
    do_run_preremove(root, packagename)

    # retrieve list of installed files
    lst = get_filelist(packagename)

    # delete files
    for i in lst:
        file = os.path.abspath(os.path.join(root,i))
        if not os.path.exists(file):
            sys.stderr.write('warning: %s no such file\n' % file)
        elif not os.path.isdir(file):
            try:
                os.remove(file)
            except (WindowsError, IOError) as err:
                print(err)
                os.chmod(file, 0777) # remove readonly flag and try again
                os.remove(file)
            else:
                sys.stdout.write('removed: %s\n' % file)

    # clear from manifest
    write_filelist(packagename, [])

    # remove package details from installed.db
    del(installed[0][packagename])
    write_installed()
#@+node:maphew.20120222135111.1873: *3* do_run_preremove
def do_run_preremove(root, packagename):
    '''Run the etc/preremove batch files for this package'''
    for bat in glob.glob('%s/etc/remove/%s.bat' % (root, packagename)):
        try:
            retcode = subprocess.call(bat, shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", retcode
            print >>sys.stderr, "Post_install complete, return code", retcode

        except OSError, e:
            print >>sys.stderr, "Execution failed:", e
#@+node:maphew.20100308085005.1380: ** Getters
#@+node:maphew.20150325155203.3: *3* get_all_dependencies
def get_all_dependencies(packages, nested_deps, parent=None):
    ''' Recursive lookup for required packages in order of dependence.
        Returns an ordered list.
    '''
    if isinstance(packages, basestring): packages = [packages]

    for p in packages:
        try:
            deps = get_info(p)['requires'].split()
        except KeyError as e:
            print e.message
            print "leaving out: ", p
            continue
        if parent:
            inspos = nested_deps.index(parent)
            nested_deps.insert(inspos, p)
        else:
            nested_deps.append(p)
        deps = [x for x in deps if x not in nested_deps]
            # remove nested_deps items from deps
        if deps:
            nested_deps = get_all_dependencies(deps, nested_deps,p)

    return uniq(nested_deps)
	
def get_arch(bits=""):
    '''Determine CPU architecture to use (X86, X86_64) from --arch parameter.
       Allows `--arch 32 | 64` as well as longer `--arch x86 | x86_64` '''
    # AMR66: error encountered - changed, but: we don't need this? TODO: remove and test
    if bits:
        if '32' in bits: arch = 'x86'
        if '64' in bits: arch = 'x86_64'
    else:
        try:
            arch = setuprc['architecture']
        except KeyError:
            arch = 'x86'
    if not arch in ['x86', 'x86_64']:
        return None
    return arch
	
#@+node:maphew.20150501221304.43: *3* get_cache_dir
def get_cache_dir():
    '''Return path to use for saving downloads.

    Precedence order:
        - command line option (-c, --cache)
        - last used cache (read from setup.rc)
        - Public Downloads folder
        - Osgeo default (%osgeo4w_root%/var/...)
    '''
    if 'cache_dir' in globals() and globals()['cache_dir'] is not None:
        return globals()['cache_dir']
    if 'last_cache' in globals() and globals()['last_cache'] is not None:
        return globals()['last_cache']
    try:
        pubdown = knownpaths.get_path(getattr(knownpaths.FOLDERID, 'PublicDownloads'))
    except knownpaths.PathNotFoundException:
        # AMR66: try to use default tmp from environment,
        #        this is pretty close to osgeo4w_setup?
        pubdown = os.environ["TEMP"]

    if not os.path.exists(pubdown):
        if debug: print 'Public downloads "%s" not found, using ./var/cache instead'
        cache_dir = '%s/var/cache/setup' % (root)
    else:
        cache_dir = pubdown
    return cache_dir
#@+node:maphew.20141112222311.3: *3* get_zipfile
def get_zipfile(packagename):
    '''Return full path name of locally downloaded package archive.'''
    return dists[distname][packagename]['local_zip']
#@+node:maphew.20100223163802.3747: *3* get_installed_version
def get_installed_version(packagename):
    '''Derive version number from archive filename in 'installed' dict.'''
    return split_ball(installed[0][packagename])[1]
#@+node:maphew.20100223163802.3744: *3* get_field
def get_field(field, default=''):
    for d in (distname,) + distnames:
        if dists[d].has_key (packagename) \
           and dists[d][packagename].has_key(field):
            return dists[d][packagename][field]
    return default

#@+node:maphew.20100223163802.3745: *3* get_filelist
def get_filelist(packagename):
    ''' Retrieve list of files installed for package X from manifest (/etc/setup/package.lst.gz)'''
    os.chdir(config)
    pipe = gzip.open(config + packagename + '.lst.gz', 'r')
    lst = map(string.strip, pipe.readlines())
    if pipe.close():
        raise TypeError('urg')
    return lst

#@+node:maphew.20100223163802.3746: *3* get_installed
def get_installed():
    ''' Get list of installed packages from ./etc/setup/installed.db.

    Returns nested dictionary (empty when installed.db doesn't exist):
    {status_int : {pkg_name : archive_name}}

    I don't know significance of the nesting or leading zero. It appears to be
    extraneous? The db is just a straight name:tarball lookup table.
    In write_installed() the "status" is hard coded as 0 for all packages.
    '''
    global installed

    # I think the intent here is for performance,
    # don't reread from disk for every invocation.
    # I'm not sure that's wise. What if setup.exe
    # has modified it in the interim? Or another
    # apt instance?
    if installed:
        return installed

    installed = {0:{}}
    for i in open (installed_db).readlines()[1:]:
        name, ball, status = string.split(i)
        installed[int(status)][name] = ball
    return installed

#@+node:maphew.20100223163802.3749: *3* get_config
def get_config(fname):
    '''Open /etc/setup/fname and return contents, e.g. /etc/setup/last-cache
    '''
    f = os.path.join(config, fname)
    if not os.path.exists(f):
        return None
    else:
        value = file(f).read().strip()
        return value
#@+node:maphew.20100307230644.3848: *3* get_menu_links
def get_menu_links(bat):
    '''Parse postinstall batch file for menu and desktop links.

    Relies on shlex module which splits on spaces, yet preserves
    spaces within quotes (http://stackoverflow.com/questions/79968)
    '''
    # From 'xxmklink' lines grab first parameter, which is the link path
    # and interpret known variables.
    links = []
    for line in open(bat,'r'):

        # super ugly kludge for unmatched quotes in a specific package
        # see https://github.com/maphew/apt/issues/40
        # DO NOT LET THIS LIVE LONG, AND ESPECIALLY NOT GET RELEASED!!
        if 'ApacheMonitor.exe"' in line:
            line = line[-1]

        if 'xxmklink' in line:
            try:
                link = shlex.split(line)[1]
            except ValueError as e:
                print "Parsing error in bat %s. May causes erorrs when removing package." % bat
                link = line.split()[1]

            link = link.replace('%OSGEO4W_ROOT%',OSGEO4W_ROOT)
            link = link.replace('%OSGEO4W_STARTMENU%',OSGEO4W_STARTMENU)
            link = link.replace('%ALLUSERSPROFILE%',os.environ['ALLUSERSPROFILE'])
            link = link.replace('%USERPROFILE%',os.environ['USERPROFILE'])
            links.append(link)
    return links
#@+node:maphew.20100223163802.3751: *3* get_mirror
def get_mirror():
    if last_mirror == None:
        mirror = 'http://download.osgeo.org/osgeo4w/'
    else:
        mirror = last_mirror
    return mirror

#@+node:maphew.20100223163802.3753: *3* get_new
def get_new():
    '''Return list of mirror packages of newer versions than those installed.'''
    lst = []
    for packagename in installed[0].keys():
        remote = get_version(packagename)
        local = get_installed_version(packagename)
        remote = parse_version(version_to_string(remote))
        local = parse_version(version_to_string(local))

        if remote > local:
            lst.append(packagename)
    return lst
#@+node:maphew.20150201144500.7: *3* get_requires
def get_requires(packagename):
    ''' identify dependencies of package [deprecated]

        use get_all_dependencies() for recursive dependencies list
        and get_info(p)['requires'] for just one level
    '''
    print '+++ get_requires() is depcrecated. Please use get_all_dependencies().'
    dist = dists[distname]
    if not dists[distname].has_key(packagename):
        no_package(packagename, distname)
        #return []
        sys.exit(1)
    if depend_p:
        return [packagename]
    reqs = {packagename:0}
    n = 0
    while len(reqs) > n:
        n = len(reqs)
        for i in reqs.keys():
            if not dist.has_key(i):
                sys.stderr.write("error: %s not in [%s]\n" \
                          % (i, distname))
                if i != packagename:
                    del reqs[i]
                continue
            reqs[i] = '0'
            p = dist[i]
            if not p.has_key('requires'):
                continue
            reqs.update (dict(map(lambda x: (x, 0),
                        string.split (p['requires']))))
    return reqs.keys()
#@+node:maphew.20100223163802.3755: *3* get_special_folder
def get_special_folder(intFolder):
    ''' Fetch paths of Windows special folders: Program Files, Desktop, Startmenu, etc.

    Written by Luke Pinner, 2010. Code is public domain, do with it what you will...
    todo: look at replacing with WinShell module by Tim Golden,
    http://winshell.readthedocs.org/en/latest/special-folders.html
    '''
    import ctypes
    from ctypes.wintypes import HWND, HANDLE, DWORD, LPCWSTR, MAX_PATH, create_unicode_buffer
    SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathW
    SHGetFolderPath.argtypes = [HWND, ctypes.c_int, HANDLE, DWORD, LPCWSTR]
    auPathBuffer = create_unicode_buffer(MAX_PATH)
    exit_code=SHGetFolderPath(0, intFolder, 0, 0, auPathBuffer)
    return auPathBuffer.value.encode(locale.getpreferredencoding())
#@+node:maphew.20100223163802.3756: *3* get_url
def get_url(packagename):
    # FIXME: This looks more complicated than it needs to be.
    # If all we're after is the local url, why does the install status matter?
    # Just construct what path should be and look if file is there.
    # Or maybe the func name just doesn't accurately reflect actual purpose(?)
    if not dists[distname].has_key(packagename) \
       or not dists[distname][packagename].has_key(INSTALL):
 ##       no_package ()
        # moved here from no_package(), part of remove-globals refactoring
        sys.stderr.write("%s: %s not in [%s]\n" % ('error', packagename, distname))

        install = 0
        for d in distnames:
            if dists[d].has_key(packagename) \
               and dists[d][packagename].has_key(INSTALL):
                install = dists[d][packagename][INSTALL]
                sys.stderr.write("warning: using [%s]\n" % d)
                break
        if not install:
            sys.stderr.write("error: %s not installed\n" % packagename)
            sys.exit(1)
    else:
        install = dists[distname][packagename][INSTALL]
    filename, size, md5_sum = string.split(install)
    return filename, md5_sum
#@+node:maphew.20100223163802.3757: *3* get_version
def get_version(packagename):
    if not dists[distname].has_key(packagename) \
       or not dists[distname][packagename].has_key(INSTALL):
        no_package(packagename, distname)
        return (0, 0)

    package = dists[distname][packagename]
    if not package.has_key('ver'):
        file = string.split(package[INSTALL])[0]
        ball = os.path.split(file)[1]
        package['ver'] = split_ball(ball)[1]
    return package['ver']

#@+node:maphew.20100308085005.1381: ** Writers
#@+node:maphew.20100223163802.3750: *3* save_config
def save_config(fname,values):
    # '''save settings like last-mirror, last-cache'''
    # e.g. /etc/setup/last-cache --> d:\downloads\osgeo4w
    return "save_config() is deprecated. Please rewrite to use write_setuprc()"

    os.chdir(config)
    pipe = open(fname,'w')

    for i in values:
        pipe.write (i)
    if pipe.close ():
        raise TypeError('urg')
#@+node:maphew.20100223163802.3764: *3* write_installed
def write_installed ():
    ''' Record installed packages in install.db '''
    file = open (installed_db, 'w')
    file.write (installed_db_magic)
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise TypeError('urg')
#@+node:maphew.20100223163802.3766: *3* write_filelist
def write_filelist (packagename, lst):
    # ''' Record installed files in package manifest (etc/setup/packagename.lst.gz) '''
    os.chdir(config)
    pipe = gzip.open (packagename + '.lst.gz','w')

    for i in lst:
        pipe.write (i)
        pipe.write ('\n')
    if pipe.close ():
        raise TypeError('urg')
#@+node:maphew.20141130225434.5: *3* write_setuprc
def write_setuprc(setuprc, fname='setup.rc'):
    '''Write the setuprc dictionary to file, in osgeo4w-setup.exe format.

    Dict entries with empty values are left out.

    Incoming dict:
        last-mode: None
        last-mirror: http://download.osgeo.org/osgeo4w/
        net-method: None
        last-cache: C:\Users\Matt\Downloads
        last-menu-name: OSGeo4W_default

    Out etc/setup/setup.rc:
        last-mirror
                http://download.osgeo.org/osgeo4w/
        last-cache
                C:\Users\Matt\Downloads
        last-menu-name
                OSGeo4W_default
    '''
    if not 'last-mirror' in setuprc.keys():
        return "Incoming setuprc dict doesn't have expected values, aborting"

    fname = os.path.join(config, fname)

    f = open(fname, 'w')
    for k,v in setuprc.items():
        if v:
            f.write('{0}\n\t{1}\n'.format(k,v))
    f.close()

    if debug:
        print '\n---- DEBUG: %s -----' % sys._getframe().f_code.co_name
        print "Wrote %s" % fname
        print '-' * 40
#@+node:maphew.20100308085005.1382: ** Parsers
#@+node:maphew.20141128231605.7: *3* parse_setuprc
def parse_setuprc(fname):
    '''Parse setup.rc config file into a dictionary.

    We assume any line beginning with a tab is a value, and all others are dict
    keys. Consequently this will return a bad dict if there are extra lines
    starting with tabs.

    Example C:\OSGeo4W\etc\setup\setup.rc:

        mirrors-lst
                http://download.osgeo.org/osgeo4w/;OSGeo;USA;California
        window-placement
                44,0,0,0,0,0,0,0,1,0,0,0,255,255,255,255,255,255,255,255...
        last-mode
                Advanced
        last-mirror
                http://download.osgeo.org/osgeo4w/
        net-method
                Direct
        last-cache
                C:\Users\Matt\Downloads
        last-menu-name
                OSGeo4W_default

    And result:

        last-cache:     C:\Users\Matt\Downloads
        last-mirror:    http://download.osgeo.org/osgeo4w/
        mirrors-lst:    http://download.osgeo.org/osgeo4w/;OSGeo;USA;Cal...
        window-placement:       44,0,0,0,0,0,0,0,1,0,0,0,255,255,255,255...
        last-mode:      Advanced
        last-menu-name: OSGeo4W_default
        net-method:     Direct
    '''
    d = {}
    default_keys = ['last-cache', 'last-mirror', 'mirrors-lst',
        'window-placement', 'last-mode', 'last-menu-name', 'net-method', ]

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
#@+node:maphew.20141111130056.4: *3* get_info
def get_info(packagename):
    '''Retrieve details for package X.

    Returns dict of information for the package from dict created by parse_setup_ini()
    (category, version, archive name, etc.)
    '''

    try:
        d = dists[distname][packagename]
    except KeyError:
        raise KeyError('*** Package "{}" not found in distribution "{}"'.format(packagename, distname))

    d['name'] = packagename
    #print d    # debug peek at incoming dict

    d = set_extended_info(d)

    d['filename'] = os.path.basename(d['zip_path'])

    # ensure requires key exists even if it's empty
    if not 'requires' in d.keys():
        d['requires'] = ''

    if packagename in installed[0].keys():
        d['installed'] = True
        d['install_v'] = version_to_string(get_installed_version(packagename))
            # don't like key name, but...
    else:
        d['installed'] = False

    return d

#@+node:maphew.20150418200003.11: *4* set_extended_info
def set_extended_info(d):
    """set extended information into package-info-dictionary, as used by
    get_info() or parse_setup_ini()

    We take compound values in single keys and explode them into their own keys.

        {'install': 'x86/release/gdal/gdal-1.11.1-4.tar.bz2 5430991 3b60f036f0d29c401d0927a9ae000f0c'}

    becomes:

        {'zip_path': 'x86/release/gdal/gdal-1.11.1-4.tar.bz2'}
        {'zip_size':'5430991'}
        {'md5':'3b60f036f0d29c401d0927a9ae000f0c'}
    """
    try:
        # 'install' and 'source keys have compound values, atomize them
        d['zip_path'],d['zip_size'],d['md5'] = d['install'].split()

    except KeyError as e:
        d['zip_path'],d['zip_size'],d['md5'] = ('', '', '')
        if debug:
          print "\n*** Warning: '%s' is missing %s entry in setup.ini. This might cause problems.\n" % (d['name'], e)
    except Exception as e:
        print "unknown error parsing package", d
        print "*** %s" % e.message
        d['zip_path'],d['zip_size'],d['md5'] = ('', '', '')

    try:
        d['src_zip_path'],d['src_zip_size'],d['src_md5'] = d['source'].split()
        if not debug:
            del d['source']
    except KeyError as e:
        d['src_zip_path'],d['src_zip_size'],d['src_md5'] = ('', '', '')
    except Exception as e:
        print "unknown error", d
        print "*** %s" % e.message
        d['src_zip_path'],d['src_zip_size'],d['src_md5'] = ('', '', '')

    #based on current mirror, might be different from when downloaded and/or installed
    d['local_zip'] = os.path.normpath(os.path.join(downloads, d['zip_path']))
    d['mirror_path'] = '%s/%s' % (mirror, d['zip_path'])

    return d
#@+node:maphew.20100223163802.3754: *3* parse_setup_ini

def get_setup_arch(setup_ini):
    '''Return CPU architecture used in setup.ini'''
    arch = ''
    with open(setup_ini) as f:
        for line in f:
            if "arch:" in line:
                 arch = string.strip(line.split(':')[1])
                 break
    f.close()
    return arch

def parse_setup_ini(fname):
    '''Parse setup.ini into package name, description, version, dependencies, etc.

    Args:
        fname: full path to setup.ini

    Returns:
        A nested dictionary: {Distribution {Program_name{['category', 'source', 'ldesc', 'version', 'install', 'sdesc', 'requires']}}}

        {curr {
            'gdal' {
                'name': 'gdal',
                'version': '1.11.1-4',
                'category': 'Libs Commandline_Utilities',
                etc... }
            }}
    '''
    # global dists
    dists = {'test': {}, 'curr': {}, 'prev': {}}

    chunks = string.split(open(fname).read(), '\n\n@ ')
    for i in chunks[1:]:
        lines = string.split(i, '\n')
        name = string.strip(lines[0])
        if debug and verbose:
            print 'package: ' + name
        packages = dists['curr']
        records = {'sdesc': name}
        j = 1
        while j < len(lines) and string.strip(lines[j]):
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
                key, value = map(string.strip,
                      string.split(lines[j], ': ', 1))
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

    # this duplicated from get_info()
    # ...in order to populate keys built from 'install' and 'source'
    # FIXME: apply DRY and split into smaller re-usable functions
    for p in packages:
        # print p
        # print dists[distname][p]['install']

        # AMR66: error when using distname 'test'
        # is the dict bad organized with distname as a first key?
        # what about dists[p][distname]
        # d = dists[distname][p]
        d = dists[distname][p] if dists[distname].has_key(p) else None
        if d:
            d['name'] = p

            d = set_extended_info(d)

            # insert the parsed fields back into parent dict
            dists[distname][p] = d

    # # print dists[distname]['gdal'].keys()
    return dists
#@+node:maphew.20100223163802.3760: *3* join_ball
def join_ball(t):
    return t[0] + '-' + version_to_string(t[1])

#@+node:maphew.20100223163802.3761: *3* split_ball
def split_ball(filename):
    '''Parse package archive name into a) package name and b) version numbers tuple (to feed into version_to_string)

    mc-4.6.0a-20030721-12.tar.bz2

        mc              --> package name
        4.6.0a-20030721 --> upstream application version
        12              --> package version

    python-numpy-2.7-1.5.1-1.tar.bz2

        python-numpy  --> package name
        2.7-1.5.1     --> upstream application version
        1             --> package version

    returns:

      ('mc', (4, 6, 0a, 20030721, 12))
      ('python-numpy', (2, 7, 1, 5, 1, 1))
    '''
    regex = re.compile('''
       ^       	    # beginning of line
       ([^.]*) 	    # package name: any char except period, and any amount of them, "python-numpy"
       -                # name/version delimiter
       (
           [0-9].*    # application version: any number followed by any char, any amount of them, "4.6.0a-20030721"
           -[0-9]*    # package version: dash followed by number, "-12"
           )
       .*               # accept any trailing chars after the package version
       (\.tar\.bz2)?$
       ''', re.VERBOSE)

    m = re.match(regex, filename)
    if not m:
        print '\n\n*** Error parsing version number from "%s"\n%s\n' % (filename, m)
        # amr66-patch-1: return is missing
        return "u", "0"

    return (m.group(1), string_to_version(m.group(2)))
#@+node:maphew.20100223163802.3762: *3* string_to_version
def string_to_version(s):
    # bash-2.05b-9
    # return map (string.atoi, (string.split (re.sub ('[.-]', ' ', s))))
    s = re.sub('([^0-9][^0-9]*)', ' \\1 ', s)
    s = re.sub('[ .-][ .-]*', ' ', s)
    def try_atoi(x):
        if re.match('^[0-9]*$', x):
            return string.atoi(x)
        return x
    return tuple(map(try_atoi,(string.split(s))))

#@+node:maphew.20100223163802.3763: *3* version_to_string
def version_to_string(t):
    #return '%s-%s' % (string.join (map (lambda x: "%d" % x, t[:-1]), '.'),
    #         t[-1])
    def try_itoa(x):
        if type(x) == int:
            return "%d" % x
        return x
    return '%s-%s' % (string.join(map(try_itoa, t[:-1]), '.'), t[-1])

#@+node:maphew.20100223163802.3758: ** no_package
def no_package (packagename, distname, s='error'):
    sys.stderr.write ("Warning: %s not in distribution [%s]\n" % (packagename, distname))

#@+node:maphew.20100302221232.1486: ** psort (disabled)
#def psort (lst): #Raises "AttributeError: 'function' object has no attribute 'sort'" use sorted() instead
#    plist.sort (lst)
#    return lst
#@+node:maphew.20100223163802.3765: ** post_install
def post_install(packagename):
    ''' Run postinstall batch files and update package manifest
        to catch those files not included in the package archive.
        (manifest = etc/setup/pkg-foo.lst.gz)

    adapted from "17.1.3.3 Replacing os.system()"
    http://www.python.org/doc/2.5.2/lib/node536.html
    '''

    os.chdir(root)

    # necessary for textreplace, xxmklink
    os.putenv('PATH', '%s\\bin' % os.path.normpath(OSGEO4W_ROOT))

    for bat in glob.glob('%s/etc/postinstall/*.bat' % root):
        try:
            # run the postinstall batch files
            retcode = subprocess.call(bat, shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode

            # then update manifest
            else:
                # mark bat as completed
                done_bat = bat + '.done'
                if os.path.exists(done_bat):
                    os.remove(done_bat)
                os.rename(bat, done_bat)

                # harmonize path conventions
                # TODO: Move/merge this to cyg_path helper function
                bat = bat.replace(root, '')         # strip C:\osgeo4w
                bat = bat.replace('\\','/')         # backslash to foreslash
                bat = bat.replace('/etc/', 'etc/')  # strip leading slash

                # foo.bat --> foo.bat.done in manifest
                lst = get_filelist(packagename)

                # ticket #281, ignore leading dot slash in filenames (./foo.bat --> foo.bat)
                lst = [x.replace('./','') for x in lst]

                if bat in lst:
                    lst.remove(bat)
                    lst.append(bat + '.done')
                else:
                    print """\nwarning: adding %s to install manifest failed.
                    It will need to be removed manually when uninstalling or upgrading this package""" % done_bat

                # retrieve menu & desktop links from postinstall bats
                for link in get_menu_links(done_bat):
                    lst.append(link)

                for s in lst:
                    # bin/bar.bat.tmpl --> both bin/bar.bat and bin/bar.bat.tmpl in manifest
                    if s.endswith('.tmpl'):
                         lst.append(s.replace('.tmpl',''))
                    # catch bat's which are made for py's post install
                    if s.startswith('bin/') and s.endswith('.py'):
                        p =  re.compile(r'^bin/(.*?)\.py$', re.VERBOSE)
                        out = p.sub(r'bin/\1.bat', s)
                        lst.append(out)

                write_filelist(packagename, lst)

                print >>sys.stderr, "Post_install complete, return code", retcode

        except OSError, e:
            print >>sys.stderr, "Execution failed:", e
#@+node:maphew.20100223163802.3771: ** Building from source
#@+node:maphew.20100223163802.3767: *3* do_unpack

###########################
##TODO: remove do_unpack, do_build, build, source ??
## osgeo4w does not provide a build environment
## but maybe will later?
#FIXME: pythonize gzip, tar, etc.
def do_unpack ():
    # find ball
    ball = get_ball ()
    # untar capture list
    # tarfile
    #pipe = os.popen ('tar -C %s -xjvf %s' % (CWD, ball), 'r')

    global packagename
    basename = os.path.basename (ball)
    packagename = re.sub ('(-src)*\.tar\.(bz2|gz)', '', basename)

    if os.path.exists ('%s/%s' % (SRC, packagename)):
        return

    pipe = os.popen ('tar -C %s -xjvf %s' % (SRC, ball), 'r')
    lst = map (string.strip, pipe.readlines ())
    if pipe.close ():
        raise TypeError('urg1')
    print ('%s/%s' % (SRC, packagename))
    if not os.path.exists ('%s/%s' % (SRC, packagename)):
        raise TypeError('urg2')

#@+node:maphew.20100223163802.3768: *3* do_build
def do_build ():
    src = '%s/%s' % (SRC, packagename)
    if not os.path.exists (src):
        raise TypeError('urg')

    m = re.match ('^(.*)-([0-9]*)$', packagename)
    if not m:
        raise TypeError('urg')
    namever = m.group (1)

    package = split_ball (packagename)
    name = package[0]
    #namever = name + '-' + string.join (package[1][1:-1], '.')
    pbuild = package[1][-1]

    # ugh: mknetrel should source <src>/cygwin/mknetrel
    # copy to mknetrel's EXTRA dir for now
    cygwin = src + '/cygwin'
    script = cygwin + '/mknetrel'
    if os.path.exists (script):
        shutil.copy (script, '%s/%s' % (EXTRA, namever))

    os.system ('mknetrel %s' % namever)

#@+node:maphew.20100223163802.3769: *3* build
def build ():
    # commented docstring hides this unused function from usage message
    # '''build package from source in CWD'''
    global packagename
    if not packagename:
        packagename = os.path.basename (CWD)
    do_build ()

#@+node:maphew.20100223163802.3770: *3* source
def source ():
    # commented docstring hides this unused function from usage message
    # '''download, build and install'''
    global packagename
    # let's not do dependencies
    #for packagename in missing.keys ():
    global INSTALL
    INSTALL = 'source'
    for packagename in packages:
        download ()
    for packagename in packages:
        do_unpack ()
        do_build ()
    if 1 or download_p:
        sys.exit (0)


#@-others
sys.excepthook = exceptionHandler

if __name__ == '__main__':
    #@+<<globals>>
    #@+node:maphew.20100307230644.3841: ** <<globals>>
    depend_p = 0
    download_p = 0
    command = ""
    setup_ini = ""
    distname = ""
    start_menu_name = 'OSGeo4W'
    debug = False
    verbose = False
    distname = 'curr'
    dists = 0
    distnames = ('curr', 'test', 'prev')
    bits = ""
    root = ''
    #@-<<globals>>
    #@+<<parse command line>>
    #@+node:maphew.20100307230644.3842: ** <<parse command line>>
    (options, params) = getopt.getopt (sys.argv[1:],
                      'c:dhi:m:r:t:s:xvb:',
                      ('cache=', 'download', 'help', 'mirror=', 'root=',
                       'ini=', 't=', 'start-menu=', 'no-deps',
                       'debug', 'verbose', 'bits='))
    # the first parameter is our action,
    # and change `list-installed` to `list_installed`
    if len(params) > 0:
        command = params[0].replace('-','_')
    else:
        command = 'help'

    # and all following are package names
    packages = params[1:]

    #command aliases
    uninstall = remove
    if command == 'list':
        command = 'list_installed' # don't collide with list() function

    for i in options:
        o = i[0]
        a = i[1]

        if 0:
            pass

        elif o == '--bits' or o == '-b':
            # translate bitness to CPU architecture: 32 --> x86, 64 --> x86_64
            # if user option is wrong we set empty
            a = a.lower()
            if o == '--bits' or o =='-b':
                bits = 'x86' if a == '32' else 'x86_64' if a == '64' else ''
        elif o == '--cache' or o == '-c':
                cache_dir = a
        elif o == '--download' or o == '-d':
                download_p = 1
        elif o == '--help' or o == '-h':
            command = 'help'
            break
        elif o == '--ini' or o == '-i':
            if os.path.exists(a):
                setup_ini = a
            else:
                setup_ini = urllib.urlretrieve(a)[0]
        elif o == '--mirror' or o == '-m':
            mirror = a
        elif o == '--root' or o == '-r':
            root = a
        elif o == '--t' or o == '-t':
            distname = a if a in distnames else 'curr'
        elif o == '--no-deps' or o == '-x':
            depend_p = 1
        elif o == '--start-menu' or o == '-s':
            start_menu_name = a
        elif o == '--debug':
            debug = True
        elif o == '--verbose' or o == '-v':
            verbose = True
    #@-<<parse command line>>
    
    ## BUG? I don't see `o4w=` being used here, but is optional param in function. TODO.
    ## amr66: root is not set, take default env
    OSGEO4W_ROOT = check_env(root) # look for root in environment
    if not root:
        root = OSGEO4W_ROOT

    CWD = os.getcwd()
    INSTALL = 'install'
    installed = 0

    config = root + '/etc/setup/'
    if not setup_ini:
        setup_ini = config + '/setup.ini'
    setup_bak = config + '/setup.bak'
    installed_db = config + '/installed.db'
    installed_db_magic = 'INSTALLED.DB 2\n'

    # # reverse engineering the globals...
    # # after parse_setup_ini() 'dists' is actually contents of setup.ini in a dict
    # # 'distname' is always 'current' (at present)
    # #
    # print type(dists)
    # print(distname)

    # Thank you Luke Pinner for answering how to get path of "Start > Programs"
    # http://stackoverflow.com/questions/2216173
    #PROGRAMS=2
    ALLUSERSPROGRAMS=23
    OSGEO4W_STARTMENU = get_special_folder(ALLUSERSPROGRAMS) + "\\" + start_menu_name
    os.putenv('OSGEO4W_STARTMENU', OSGEO4W_STARTMENU)

    #@+<<post-parse globals>>
    #@+node:maphew.20100307230644.3844: ** <<post-parse globals>>

    setuprc = parse_setuprc(config + '/setup.rc')
    try:
        last_mirror = setuprc['last-mirror']
        last_cache = setuprc['last-cache']
    except KeyError:
        last_mirror = None
        last_cache = None

    if not 'mirror' in globals():
        mirror = get_mirror()

    # convert mirror url into acceptable folder name
    mirror_dir = requests.utils.quote(mirror, '').lower()
        # optional quote '' param is to also substitute slashes etc.

    cache_dir = get_cache_dir()

    downloads = '%s/%s' % (cache_dir, mirror_dir)

    if debug:
        print '\n---- DEBUG: %s ----' % sys._getframe().f_code.co_name
        print 'last-mirror:', last_mirror
        print 'last-cache:', last_cache
        print "Using mirror:\t", mirror
        print "Saving to:\t", cache_dir
        print '-' * 40
    #@-<<post-parse globals>>
    #@+<<run the commands>>
    #@+node:maphew.20100307230644.3843: ** <<run the commands>>
    if command == 'setup':
        if not bits:
            sys.stderr.write("error: `--bits` is required parameter for Setup\n")
            
        # AMR66: what if setup is called again, but with wrong "bits" flag
        if os.path.exists(setup_ini):
            print "Warning! Setup was already done for %s"%OSGEO4W_ROOT
            arch = get_setup_arch(setup_ini)
            if arch != bits:
                sys.stderr.write("error: Architecture mismatch! Setup.ini: '%s', Command line: '%s'\n" % 
                                 (arch, bits))
                sys.exit(2)
                
        setup(OSGEO4W_ROOT)        
        # AMR66: removed - setup.rc will not be written if we exit here
        # sys.exit(0)

    elif command == 'help':
        help(params)

    else:
        # print 'check_setup reached'
        # AMR66: osgeo_setup.exe does not hold a copy under setup_ini
        # we want compatibility, so this must be changed:
        check_setup(installed_db, setup_ini)
        
        arch = get_setup_arch(setup_ini)
        # set bits to arch in setup_ini, if not set
        if not bits:
            bits = arch
        # is set but missmatched with setup_ini
        if not bits == arch:
            sys.stderr.write("error: Architecture mismatch! Setup.ini: '%s', Command line: '%s'\n" % (arch, bits))
            sys.exit(2)
        if debug:
            print "Architecture: we are in an %s installation" % arch
        
        #fixme: these setup more globals like dists-which-is-really-installed-list
        #that are hard to track later. Should change to "thing = get_thing()"
        dists = parse_setup_ini(setup_ini)
        get_installed()

        if command == 'update':
            update()
        elif command and command in __main__.__dict__:
            __main__.__dict__[command] (packages)
        else:
            print '"%s" not understood, please run "apt help"' % command
    #@-<<run the commands>>
    #@+<<wrap up>>
    #@+node:maphew.20100307230644.3845: ** <<wrap up>>
    save_config('last-mirror', mirror)      # deprecated
    save_config('last-cache', cache_dir)    # deprecated

    setuprc['last-mirror'] = mirror
    setuprc['last-cache'] = cache_dir
    write_setuprc(setuprc)
    #@-<<wrap up>>
#@-leo
