#@+leo-ver=5-thin
#@+node:maphew.20141101222700.7: * @file setup-parser.py
root = 'b:/o4w'
config = root + '/etc/setup/'
setup_ini = config + '/setup.ini'

def parse_setup(fname):
    chunks = string.split(open(fname).read(), '\n\n@ ') #record delimiter
    print chunks
    for i in range(0,4):
        print

if __name__ == '__main__':
    parse_setup(setup_ini)
#@-leo
