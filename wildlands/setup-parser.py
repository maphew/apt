#@+leo-ver=5-thin
#@+node:maphew.20141101222700.7: * @file setup-parser.py
import string

root = 'b:/o4w'
config = root + '/etc/setup/'
setup_ini = config + '/setup.ini'

#@+others
#@+node:maphew.20141101232552.4: ** parse_setup
def parse_setup(fname):
    chunks = string.split(open(fname).read(), '\n\n@ ') #record delimiter
    
    # first one is header
   # print '--- Chunk %s ---\n%s' % (0, chunks[0])

    ini_d = {}
    for i in range(1,5):
        #print '--- Chunk %s ---\n%s' % (i, chunks[i])
        pkg_d = pkg_to_dict(chunks[i])
        ini_d.update(pkg_d)
        #print '\t--- Out ---'
        #print '\t%s' % pkg_d
    
    print ini_d.keys()
    #print ini_d.values()
#@+node:maphew.20141101232552.8: *3* @
#@+at
# for i in chunks[1:]:
#     name = string.strip(lines[0])
#     debug('package: ' + name)
#     lines = string.split(i, '\n')
#     packages = dists['curr']
#     records = {'sdesc': name}
#@+node:maphew.20141101232552.6: ** pkg_to_dict
def pkg_to_dict(chunk):
    ''' Take one package record from setup.ini and parse into nested dictionary.
    
    ------ ini record -----
        @apache
        sdesc: "Apache Web Server"
        ldesc: "Apache Web Server"
        category: Web
        requires: shell php
        version: 2.2.14-4
        install: x86/release/apache/apache-2.2.14-4.tar.bz2 2453154 dcc24008f878e26084be298c09e6c9b3
        [prev]
        version: 2.2.14-3
        install: x86/release/apache/apache-2.2.14-3.tar.bz2 2453132 78f5c2e707af63a6a77763eec0080433
        
    ----- Dictionary returned (just keys listed below) -----
        Package dict ['apache']
        Values dict ['category', 'name', 'sdesc', 'ldesc', 'version', 'install', 'requires']            
        
    All lines after [prev]/[test]/[...] are ignored at the moment.
    '''
    #print '----- pkg_to_dict -----'
    lines = chunk.split('\n')
    name = lines[0]
    pkg_d,val_d = {},{}
    val_d['name'] = name
    for i in range(1, len(lines)):
        #print lines[i]
        if lines[i][0] == '[':  # stop on [prev], [test], etc.
            break
        key, value = lines[i].split(':')
        val_d[key] = string.strip(value)
        
    pkg_d[val_d['name']] = val_d
    
    #print 'Package dict', pkg_d.keys()
    #print 'Values dict', val_d.keys()
    return pkg_d
#@+node:maphew.20141101232552.3: ** get_info
def get_info(packagename):
    '''Retrieve details for package X.
    
    Returns dict of information for the package from setup.ini (category, version, archive name, etc.)
    '''
    d = dists[distname][packagename]
    d['name'] = packagename
    
    # 'install' key has compound values, atomize it.
    d['zip_path'],d['zip_size'],d['md5'] = d['install'].split()
    del d['install']
    
    #based on current mirror, which might be different from when downloaded
    d['local_zip'] = '%s/%s' % (downloads, d['zip_path'])
        
    return d
#@+node:maphew.20141101232552.5: ** get_setup_ini
def get_setup_ini():
    '''Parse setup.ini into package name, description, version, dependencies, etc.'''
    global dists
    if dists:
       # best I can figure, this is to skip redundant parsing,
       # however I don't see anywhere get_setup_ini() is
       # called more than once; candidate for removal
       print 'dists defined, skipping parse of setup.ini'
       return
    dists = {'test': {}, 'curr': {}, 'prev' : {}}
    chunks = string.split(open(setup_ini).read(), '\n\n@ ')
    for i in chunks[1:]:
        lines = string.split(i, '\n')
        name = string.strip(lines[0])
        debug('package: ' + name)
        packages = dists['curr']
        records = {'sdesc': name}
        j = 1
        while j < len(lines) and string.strip(lines[j]):
            debug('raw: ' + lines[j])
            if lines[j][0] == '#':
                j = j + 1
                continue
            elif lines[j][0] == '[':
                debug('dist: ' + lines[j][1:5])
                packages[name] = records.copy()
                packages = dists[lines[j][1:5]]
                j = j + 1
                continue

            try:
                key, value = map(string.strip,
                      string.split(lines[j], ': ', 1))
            except:
                print lines[j]
                raise TypeError('urg')
            if value[0] == '"' and value.find('"', 1) == -1:
                while 1:
                    j = j + 1
                    value += lines[j]
                    if lines[j].find('"') != -1:
                        break
            records[key] = value
            j = j + 1
        packages[name] = records
#@-others

if __name__ == '__main__':
    parse_setup(setup_ini)
    get_setup_ini()
#@-leo
