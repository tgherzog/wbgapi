
import wbgapi as w

def list():
    '''Iterate over the list of time elements in the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.time.list():
            print(elem['id'], elem[' value'])

    '''
    return w.source.features('time')
