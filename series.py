
import wbgapi as w

def list(id='all'):
    '''Iterate over the list of indicators/series in the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.series.list():
            print(elem['id'], elem['value'])

    '''
    return w.source.features('series', w.queryParam(id))

def get(id):
    '''Get a single indicator object

    Parameters:
        id:     The object ID

    Returns:
        A database object

    Example:
        print(wbgapi.series.get('SP.POP.TOTL')['value'])
    '''

    return w.source.feature('series', id)

