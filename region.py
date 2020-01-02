
import wbgapi as w
import builtins

# Here's a object-oriented approach we may use someday, but I'm not sure it's especially practial
# to implement just have list and get return Region(row) instead of row
class Region(dict):
    @property
    def members(self):
        return members(self['code'])

def list(id='all',group=None):
    '''Return a list of regions

    Parameters:
        id:         a region identifier or list-like of identifiers

        group:      subgroup to return. Can be one of: 'admin', 'geo', 'allincomelevels', 'demodividend', 'smallstates', 'other'
                    NB: technically possible to pass 'lending' but the returned values generally aren't useful

    Returns:
        a generator object
    '''

    params = {'type': group} if group else {}
    url = '{}/{}/region/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    for row in w.fetch(url, params):
        yield row

def get(id):
    
    url = '{}/{}/region/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    return w.get(url)

def members(id,param='region'):
    '''Return a set of members for the requested region

    Notes:
        the returned members may not match the economies in the current database since we access the universal region lists from the API
    '''

    e = set()
    url = '{}/{}/country'.format(w.endpoint, w.lang)
    for row in w.fetch(url, {param: id}):
        e.add(row['id'])

    return e

def Series(id='all', group=None, name='RegionName'):
    '''Return a pandas series for the requested region
    '''

    return w.pandasSeries(builtins.list(list(id, group=group)), key='code',value='name', name=name)

def info(id='all',group=None):
    w.printInfo(builtins.list(list(id,group=group)), 'code', 'name')
