
'''Access information about series in a database
'''

import wbgapi as w
from . import series_metadata as metadata
import builtins

def list(id='all'):
    '''Return a list of series elements in the current database

    Arguments:
        id:     a series identifier (i.e., CETS code) or list-like

    Returns:
        a generator object

    Example:
        for elem in wbgapi.series.list():
            print(elem['id'], elem['value'])

    '''
    return w.source.features('series', w.queryParam(id, 'series'))

def get(id):
    '''Retrieve a specific series object

    Arguments:
        id:     the series identifier

    Returns:
        a series object

    Example:
        print(wbgapi.series.get('SP.POP.TOTL')['value'])
    '''

    return w.source.feature('series', id)

def info(id='all'):
    '''Print a user report of series. This can be time consuming
    for large databases like the WDI if 'all' series are requested.

    Arguments:
        id:         a series identifier or list-like of identifiers

    Returns:
        None
    '''

    w.printInfo(builtins.list(list(id)))
