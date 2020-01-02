
import wbgapi as w
import builtins

def list(id='all'):
    '''Return a list of income levels

    Parameters:
        id:         an income identifier or list-like of identifiers

    Returns:
        a generator object
    '''

    url = '{}/{}/incomelevel/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    for row in w.fetch(url):
        yield row

def get(id):
    
    url = '{}/{}/incomeLevel/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    return w.get(url)

def members(id):
    '''Return a set of members for the requested incomelevel

    Notes:
        the returned members may not match the economies in the current database since we access the universal region lists from the API
    '''

    return w.region.members(id, 'incomelevel')

def info(id='all'):
    w.printInfo(builtins.list(list(id)))
