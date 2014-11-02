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
    print '--- Chunk %s ---\n%s' % (0, chunks[0])

    for i in range(1,5):
        print '--- Chunk %s ---\n%s' % (i, chunks[i])
        pkg_to_dict(chunks[i])
    
    # print    
    # record = chunks[3].split('\n')
    # #print record, '\n'
    # name = record[0]
    
#@+node:maphew.20141101232552.7: *3* @
#@+at
#     # build a list of dictionaries
#     packages = []
#     for r in records:
#         program = {"name":"apache", "category":"web"}
#         packages.append(program)
# 
# also http://stackoverflow.com/questions/26697475/name-a-dictionary-from-a-variable-value
#@@c
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
    print '----- pkg_to_dict -----'
    record = chunk.split('\n')
    name = record[0]
    d = {}
    d['name'] = name
    for i in range(1, len(record)):
        print record[i]
        if record[i][0] == '[':             # stop on [prev], [test], etc.
            break
        key, value = record[i].split(':')
        d[key] = string.strip(value)
        
    # now we take our internal-to-function dict, make it global, and
    # name it the same as our package name
    globals()[name] = d
    print name, eval(name)
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
#@-leo
