
'''Access information about World Bank regions
'''
import wbgapi as w
import builtins

def list(id='all',group=None):
    '''Return a list of regions

    Parameters:
        id:         a region identifier or list-like of identifiers

        group:      subgroup to return. Can be one of: 'admin', 'geo', 'allincomelevels', 'demodividend', 'smallstates', 'other'
                    NB: technically possible to pass 'lending' but the returned values generally aren't useful

    Returns:
        a generator object

    Example:
        regions = {row['code']: row['name'] for row in wbgapi.region.list()}
            
    '''

    params = {'type': group} if group else {}
    url = '{}/{}/region/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    for row in w.fetch(url, params):
        yield row

def get(id):
    '''Retrieve the specified region

    Parameters:
        id:         the region ID

    Returns:
        a region object

    Example:
        print(wbgapi.region.get('NAC')['name'])
    '''
    
    
    url = '{}/{}/region/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    return w.get(url)

def members(id,param='region'):
    '''Return a set of economy identifiers that are members of the specified region

    Parameters:
        id:     a region identifier

        param:  used internally

    Returns:
        a set object of economy identifiers

    Notes:
        the returned members may not match the economies in the current database since we access the universal region lists from the API
    '''

    e = set()
    url = '{}/{}/country'.format(w.endpoint, w.lang)
    for row in w.fetch(url, {param: id}):
        e.add(row['id'])

    return e

def Series(id='all', group=None, name='RegionName'):
    '''Return a pandas Series object for the requested regions

    Parameters:
        id:         a region identifier or list-like of identifiers

        group:      subgroup to return. See list() for possible values

        name:       the Series column name

    Returns:
        a pandas Series object
    '''

    return w.pandasSeries(builtins.list(list(id, group=group)), key='code',value='name', name=name)

def info(id='all',group=None):
    '''Print a user report of regions.

    Parameters:
        id:         a region identifier or list-like of identifiers

        group:      subgroup to return. See list() for possible values

    Returns:
        None
    '''

    w.printInfo(builtins.list(list(id,group=group)), 'code', 'name')
