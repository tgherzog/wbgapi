
'''Access information about the database's time dimension

The temporal concepts in most World Bank databases are named 'time' but in
some cases are named 'year' or something else. Keys for time elements are
not always consistent across databases. The wbgapi module tries to insulate
the user from most of these inconsistencies. The module will also generally
accept both numeric values and element keys as parameters where this is possible,
e.g., 'YR2015,' '2015' and 2015 are acceptable.
'''
import wbgapi as w
from . import utils
import builtins

# this is an array of reverse value lookup tables
_time_values = {}

def list(id='all', q=None, db=None):
    '''Return a list of time elements in the current database

    Arguments:
        id:     a time identifier or list-like

        q:      search string (on value name)

        db:     database; pass None to access the global database

    Returns:
        a generator object

    Example:
        # fetch even-numbered time elements for a decade
        for elem in wbgapi.time.list(range(2010,2020,2)):
            print(elem['id'], elem['value'])
    '''

    q,_ = utils.qget(q)

    for row in  w.source.features('time', w.queryParam(id, 'time', db=db), db=db):
        if utils.qmatch(q, row['value']):
            yield row

def get(id, db=None):
    '''Retrieve the specified time element

    Arguments:
        id:     the time identifier

        db:     database; pass None to access the global database
        
    Returns:
        a time object

    Example:
        print(wbgapi.time.get('YR2015')['value'])
    '''

    return w.source.feature('time', w.queryParam(id, 'time', db=db), db=db)

def Series(id='all', q=None, db=None, name='TimePeriodName'):
    '''Return a pandas series by calling list
    '''

    return w.Series(list(id, q=q, db=db), name=name)

def periods(db=None):
    '''Returns a dict of time features keyed by value for the current database. This is
    primarily used internally to recognize both values and keys as equivalent
    '''
    global _time_values
    
    if db is None:
        db = w.db

    v = _time_values.get(db)
    if v is None:
        v = {}
        for row in w.source.features('time', 'all', db=db):
            v[row['value']] = row['id']

        _time_values[db] = v

    return v

def info(id='all', q=None, db=None):
    '''Print a user report of time features

    Arguments:
        id:         a time identifier or list-like

        q:          search string (on value name)

        db:         database; pass None to access the global database

    Returns:
        None
    '''

    return w.Featureset(list(id, q=q, db=db))
