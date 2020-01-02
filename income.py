
'''Access information about World Bank income groups
'''
import wbgapi as w
import builtins

def list(id='all'):
    '''Return a list of income groups

    Arguments:
        id:         an income group identifier or list-like of identifiers

    Returns:
        a generator object

    Example:
        incomeGroups = {row['id']: row['value'] for row in wbapi.income.list()}
    '''

    url = '{}/{}/incomelevel/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    for row in w.fetch(url):
        yield row

def get(id):
    '''Retrieve the specified income group

    Arguments:
        id:         the income group ID

    Returns:
        an income group object

    Example:
        print(wbgapi.income.get('LIC')['name'])
    '''
    
    url = '{}/{}/incomeLevel/{}'.format(w.endpoint, w.lang, w.queryParam(id))
    return w.get(url)

def members(id):
    '''Return a set of economy identifiers that are members of the specified income group

    Arguments:
        id:     an income group identifier

    Returns:
        a set object of economy identifiers

    Notes:
        the returned members may not match the economies in the current database since we access the universal region lists from the API
    '''

    return w.region.members(id, 'incomelevel')

def Series(id='all',name='IncomeGroupName'):
    '''Return a pandas Series object for the requested income groups

    Arguments:
        id:         an income group identifier or list-like of identifiers

        name:       the Series column name

    Returns:
        a pandas Series object
    '''

    return w.pandasSeries(builtins.list(list(id)), name=name)

def info(id='all'):
    '''Print a user report of income groups

    Arguments:
        id:         an income group identifier or list-like of identifiers

    Returns:
        None
    '''
    w.printInfo(builtins.list(list(id)))
