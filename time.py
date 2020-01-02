
import wbgapi as w
import builtins

# this is an array of reverse value lookup tables
_time_values = {}

_dimensions = {}

def list(id='all'):
    '''Iterate over the list of time elements in the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.time.list():
            print(elem['id'], elem[' value'])

    '''
    return w.source.features(dimension_name(), queryParam(id))

def periods():
    '''Returns a dict of time features keyed by value for the current database
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
    '''Helper function to discern the API name of the time dimension. This varies by database
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
    '''Prepare parameters for API query
    '''

    if type(arg) is str or type(arg) is int:
        arg = [arg]

    v = periods()
    return ';'.join(map(lambda x: str(v.get(str(x),x)), arg))

def info(id='all'):
    w.printInfo(builtins.list(list(id)))
