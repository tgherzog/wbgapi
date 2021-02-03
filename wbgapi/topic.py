
'''Access information about World Bank topics. This works best with the WDI (source=2)
but should also work okay with other databases
'''
import wbgapi as w
from . import utils
import builtins

def list(id='all', q=None):
    '''Return a list of topics

    Arguments:
        id:         a region identifier or list-like of identifiers

        q:          search string (on topic name)

    Returns:
        a generator object

    Example:
        topics = {row['value']: row['id'] for row in wbgapi.topic.list()}
            
    Notes:
        The topic list is global to the entire API and is not specific to the current database.

    '''

    q,_ = utils.qget(q)

    for row in w.fetch('topic/' + w.queryParam(id)):
        if utils.qmatch(q, row['value']):
            yield row

def get(id):
    '''Retrieve the specified topic

    Arguments:
        id:         the topic ID

    Returns:
        a topic object

    Example:
        print(wbgapi.topic.get(5)['value'])
    '''
    
    
    return w.get('topic/' + w.queryParam(id))

def members(id):
    '''Return a set of series identifiers that are members of the specified topic

    Arguments:
        id:     a topic identifier

    Returns:
        a set object of series identifiers

    '''

    e = set()
    for row in w.fetch('topic/{}/indicator'.format(w.queryParam(id)), {'source': w.db}):
        e.add(row['id'])

    return e

def Series(id='all', q=None, name='TopicName'):
    '''Return a pandas Series by calling list
    '''

    return w.Series(list(id, q=q), name=name)

def info(id='all', q=None):
    '''Print a user report of topics

    Arguments:
        id:         a region identifier or list-like of identifiers

        q:          search string (on topic name)

    Returns:
        None
            
    Notes:
        The topic list is global to the entire API and is not specific to the current database.

    '''

    return w.Featureset(list(id, q=q))
