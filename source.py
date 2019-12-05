
import wbgapi as w
import urllib


# concepts cached per database
_concepts = {}

def list():
    '''Iterate of list of databases

    Returns:
        a generator object

    Example:
        for elem in wbgapi.source.list():
            print elem['id'], elem['name'], elem['lastupdated']
    '''

    url = '{}/{}/sources'.format(w.endpoint, w.lang)

    return w.fetch(url)

def get(db=None):
    '''Retrieve the record for the specified database

    Parameters:
        db:      the database ID (e.g., 2=WDI). Default to the global db

    Returns:
        a database object

    Example:
        print wbgapi.source.get(2)['name']
    '''

    if db is None:
        db = w.wb

    url = '{}/{}/sources/{}'.format(w.endpoint, w.lang, db)
    return w.get(url)

def concepts(db=None):
    '''Retrieve the concepts for the specified database

    Parameters:
        db:     the database ID (e.g., 2=WDI). Default to the global db

    Returns:
        a dictionary of concepts: keys are URL friendly

    Notes:
        The series module uses this function to ascertain the correct name of the political-economic
        dimension of a time series database. In most cases this is 'country' but 'economy,' 'states'
        and others are used in some cases

    Example:
        for k,v in wbgapi.source.concepts(2).iteritems():
            print k, v
    '''

    global _concepts

    if db is None:
        db = w.db

    db = int(db)
    c = _concepts.get(db)
    if c is not None:
        return c

    url = '{}/{}/sources/{}/concepts'.format(w.endpoint, w.lang, db)
    c = {}
    for row in w.fetch(url):
        key = urllib.quote(row['id']).lower()
        c[key] = row['value']

    _concepts[db] = c
    return c

def features(concept, db=None):
    '''Retrieve features for the specified database

    Parameters:
        concept:    the concept to retrieve (e.g., 'series')
        db:         the database to access (e.g., 2=WDI). Default uses the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.source.features('time'):
            print elem['id'], elem['value']
    '''

    if db is None:
        db = w.db

    concept_list = concepts(db)
    if concept_list.get(concept) is None:
        return None

    url = '{}/{}/sources/{}/{}'.format(w.endpoint, w.lang, db, concept)
    return w.fetch(url)

