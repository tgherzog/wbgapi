
'''Access information about series in a database
'''

import wbgapi as w
from . import series_metadata as metadata
import builtins

def list(id='all', topic=None, db=None):
    '''Return a list of series elements in the current database

    Arguments:
        id:     a series identifier (i.e., CETS code) or list-like

        topic:  topic ID or list-like

        db:     database; pass None to access the global database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.series.list():
            print(elem['id'], elem['value'])

    '''
    if( topic ):
        topics = w.topic.members(topic)
        if type(id) is str and id != 'all':
             # if id is also specified, then calculate the intersection of that and the series from topics
             id = set(w.queryParam(id, 'series', db=db).split(';'))
             id &= topics
        else:
            id = topics

    return w.source.features('series', w.queryParam(id, 'series', db=db), db=db)

def get(id, db=None):
    '''Retrieve a specific series object

    Arguments:
        id:     the series identifier

        db:     database; pass None to access the global database

    Returns:
        a series object

    Example:
        print(wbgapi.series.get('SP.POP.TOTL')['value'])
    '''

    return w.source.feature('series', id, db=db)

def info(id='all', topic=None, db=None):
    '''Print a user report of series. This can be time consuming
    for large databases like the WDI if 'all' series are requested.

    Arguments:
        id:         a series identifier or list-like of identifiers

        topic:      topic ID or list-like

        db:         database; pass None to access the global database

    Returns:
        None
    '''

    return w.Featureset(list(id, topic=topic, db=db))
