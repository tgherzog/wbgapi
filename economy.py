
import wbgapi as w
import builtins

_dimensions = {}

def list():
    '''Iterate over the list of time elements in the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.time.list():
            print(elem['id'], elem[' value'])

    '''
    return w.source.features(dimension_name())

def dimension_name(db=None):
    '''Helper function to discern the API name of the economy dimension. This varies by database
    '''

    if db is None:
        db = w.db

    global _dimensions

    t = _dimensions.get(db)
    if t is None:
        concepts = builtins.list(w.source.concepts(db))
        for elem in ['country', 'economy', 'admin%20region', 'states', 'provinces']:
            if elem in concepts:
                t = elem
                _dimensions[db] = t
                break

    return t
