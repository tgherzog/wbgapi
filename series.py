
import wbgapi as w
from . import series_metadata as metadata
import builtins

def list(id='all'):
    '''Iterate over the list of indicators/series in the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.series.list():
            print(elem['id'], elem['value'])

    '''
    return w.source.features('series', queryParam(id))

def get(id):
    '''Get a single indicator object

    Parameters:
        id:     The object ID

    Returns:
        A database object

    Example:
        print(wbgapi.series.get('SP.POP.TOTL')['value'])
    '''

    return w.source.feature('series', id)

def queryParam(arg):
    '''Prepare parameters for an API query
    '''

    return w.queryParam(arg)

def info(id='all'):
    return w.printInfo(builtins.list(list(id)))
