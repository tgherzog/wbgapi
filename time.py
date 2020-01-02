
'''Access information about the database's time dimension

The temporal concepts in most World Bank databases are named 'time' but in
some cases are named 'year' or something else. Keys for time elements are
not always consistent across databases. The wbgapi module tries to insulate
the user from most of these inconsistencies. The module will also generally
accept both numeric values and element keys as parameters where this is possible,
e.g., 'YR2015,' '2015' and 2015 are acceptable.
'''
import wbgapi as w
import builtins

# this is an array of reverse value lookup tables
_time_values = {}

_dimensions = {}

def list(id='all'):
    '''Return a list of time elements in the current database

    Arguments:
        id:     a time identifier or list-like

    Returns:
        a generator object

    Example:
        # fetch even-numbered time elements for a decade
        for elem in wbgapi.time.list(range(2010,2020,2)):
            print(elem['id'], elem['value'])
    '''

    return w.source.features(dimension_name(), queryParam(id))

def get(id):
    '''Retrieve the specified time element

    Arguments:
        id: the time identifier
        
    Returns:
        a time object

    Example:
        print(wbgapi.time.get('YR2015')['value'])
    '''

    return w.source.feature(dimension_name(), queryParam(id))

    
def periods():
    '''Returns a dict of time features keyed by value for the current database. This is
    primarily used internally to recognize both values and keys as equivalent
    '''
    global _time_values
    
    v = _time_values.get(w.db)
    if v is None:
        v = {}
        for row in w.source.features(dimension_name(), 'all'):
            v[row['value']] = row['id']

        _time_values[w.db] = v

    return v

def dimension_name(db=None):
    '''Helper function to discern the API name of the time dimension for the specified database

    Arguments:
        db:     a database identifier; pass None to use the global database
    '''

    if db is None:
        db = w.db

    global _dimensions

    t = _dimensions.get(db)
    if t is None:
        concepts = builtins.list(w.source.concepts(db))
        for elem in ['time', 'year']:
            if elem in concepts:
                t = elem
                _dimensions[db] = t
                break

    return t

def queryParam(arg):
    '''Prepare parameters for an API query
    '''

    if type(arg) is str or type(arg) is int:
        arg = [arg]

    v = periods()
    return ';'.join(map(lambda x: str(v.get(str(x),x)), arg))

def info(id='all'):
    '''Print a user report of time features

    Arguments:
        id:         a time identifier or list-like

    Returns:
        None
    '''
    w.printInfo(builtins.list(list(id)))
