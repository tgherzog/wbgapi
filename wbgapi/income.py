
'''Access information about World Bank income groups. This works best with the WDI (source=2)
and other databases that share the same list of economies. It will probably not work
well with subnational databases or region-specific ones.
'''
import wbgapi as w
from . import utils
import builtins

def list(id='all', q=None):
    '''Return a list of income groups

    Arguments:
        id:         an income group identifier or list-like of identifiers

        q:          search string (on income group name)

    Returns:
        a generator object

    Example:
        incomeGroups = {row['id']: row['value'] for row in wbapi.income.list()}

    Notes:
        The income group list is global to the entire API and is not specific to the current database.

    '''

    q,_ = utils.qget(q)

    for row in w.fetch('incomelevel/' + w.queryParam(id)):
        if utils.qmatch(q, row['value']):
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
    
    return w.get('incomelevel/' + w.queryParam(id))

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

def Series(id='all', q=None, name='IncomeGroupName'):
    '''Return a pandas Series object by calling list
    '''

    return w.Series(list(id, q=q), name=name)

def info(id='all', q=None):
    '''Print a user report of income groups

    Arguments:
        id:         an income group identifier or list-like of identifiers

        q:          search string (on income group name)

    Returns:
        None

    Notes:
        The income group list is global to the entire API and is not specific to the current database.

    '''

    return w.Featureset(list(id, q=q))
