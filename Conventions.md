# Apt code conventions #

Not really thought out or set in stone yet, just a summary of a few patterns that seem to be crystallizing for me.

`p`: package name, usually seen in `for p in packages: ...`  

`p_info`: package info, a dictionary resulting from `get_info(p)`


Print name of current function when `--debug` active:

    if debug:
        print '\n### DEBUG: %s ###' % sys._getframe().f_code.co_name


 