
import wbgapi as w
from . import economy_metadata as metadata
import builtins

_dimensions = {}
_aggs = None

def list(id='all'):
    '''Iterate over the list of time elements in the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.time.list():
            print(elem['id'], elem[' value'])

    '''
    aggs = aggregates()
    for row in w.source.features(dimension_name(), queryParam(id)):
        row['aggregate'] = row['id'] in aggs
        yield row

def get(id):
    '''Retrieve the specified economy

    Parameters:
        id:     the economy ID

    Returns:
        a database object

    Example:
        print(wbgapi.economy.get('BRA')['value'])
    '''

    aggs = aggregates()
    row = w.source.feature(dimension_name(), id)
    row['aggregate'] = row['id'] in aggs
    return row

    
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

def queryParam(arg):
    '''Prepare parameters for an API query
    '''

    return w.queryParam(arg)

def aggregates():
    '''Returns a set object with both the 2-character and 3-character codes
    of aggregate economies. These are obtained from the API upon first call
    '''

    global _aggs

    if type(_aggs) is set:
        return _aggs

    url = '{}/country/all'.format(w.endpoint)
    _aggs = set()
    for row in w.fetch(url):
        if row['region']['id'] == 'NA':
            _aggs.add(row['id'])
            _aggs.add(row['iso2Code'])

    return _aggs
