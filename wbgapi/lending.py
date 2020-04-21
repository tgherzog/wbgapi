
'''Access information about World Bank lending groups. This works best with the WDI (source=2)
and other databases that share the same list of economies. It will probably not work
well with subnational databases or region-specific ones.
'''
import wbgapi as w
import builtins

def list(id='all'):
    '''Return a list of lending groups

    Arguments:
        id:         a lending group identifier or list-like of identifiers

    Returns:
        a generator object

    Example:
        lendingGroups = {row['id']: row['value'] for row in wbapi.lending.list()}
            
    Notes:
        The lending group list is global to the entire API and is not specific to the current database.

    '''

    for row in w.fetch('lendingtype/' + w.queryParam(id)):
        yield row

def get(id):
    '''Retrieve the specified lending group

    Arguments:
        id:         the lending group ID

    Returns:
        a lending group object

    Example:
        print(wbgapi.lending.get('IBD')['value'])
    '''
    
    return w.get('lendingtype/' + w.queryParam(id))

def members(id):
    '''Return a set of economy identifiers that are members of the specified lending group

    Arguments:
        id:     a lending group identifier

    Returns:
        a set object of economy identifiers

    Notes:
        the returned members may not match the economies in the current database since we access the universal region lists from the API
    '''

    return w.region.members(id, 'lendingtype')

def Series(id='all',name='LendingGroupName'):
    '''Return a pandas Series object for the requested lending groups

    Arguments:
        id:         a lending group identifier or list-like of identifiers

        name:       the Series column name

    Returns:
        a pandas Series object
    '''

    return w.pandasSeries(builtins.list(list(id)), name=name)

def info(id='all'):
    '''Print a user report of lending groups

    Arguments:
        id:         a lending group identifier or list-like of identifiers

    Returns:
        None
            
    Notes:
        The lending group list is global to the entire API and is not specific to the current database.

    '''

    return w.Featureset(list(id))
