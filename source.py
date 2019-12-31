
import wbgapi as w
import urllib.parse


# concepts cached per database
_concepts = {}
_metadata_flags = {}

def list(id='all'):
    '''Iterate of list of databases

    Parameters:
        id:     the database ID to return

    Returns:
        a generator object

    Example:
        for elem in wbgapi.source.list():
            print elem['id'], elem['name'], elem['lastupdated']
    '''

    return w.fetch(_sourceurl(w.queryParam(id)), {'databid': 'y'})

def get(db=None):
    '''Retrieve the record for a single database

    Parameters:
        db:      the database ID (e.g., 2=WDI). Default to the global db

    Returns:
        a database object

    Example:
        print wbgapi.source.get(2)['name']
    '''

    return w.get(_sourceurl(db), {'databid': 'y'})

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
    for row in w.fetch(url, concepts=True):
        key = urllib.parse.quote(row['id']).lower()
        c[key] = row['value']

    _concepts[db] = c
    return c

def features(concept, id='all', db=None):
    '''Retrieve features for the specified database

    Parameters:
        concept:    the concept to retrieve (e.g., 'series')
        id:         object identifiers to retrieve; must be a well-formed string
        db:         the database to access (e.g., 2=WDI). Default uses the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.source.features('time'):
            print elem['id'], elem['value']
    '''

    return w.fetch(_concepturl(concept, id, db))

def feature(concept, id, db=None):
    '''Retrieve a single feature for the specified database

    Parameters:
        concept:    the concept to retrieve (e.g., 'series')
        id:         the object ID
        db:         the database to access (e.g., 2=WDI). Default uses the current database

    Returns:
        a database object

    Example:
        print(wbgapi.source.feature('series', 'SP.POP.TOTL')['value'])
    '''

    return w.get(_concepturl(concept, id, db))

def has_metadata(db=None):
    '''Return True/False on whether the database has metadata

    Parameters:
        db:     the database to query

    Returns:
        Boolean
    '''

    if db is None:
        db = w.db

    global _metadata_flags
    m = _metadata_flags.get(db)
    if m is None:
        src = get(db)
        m = src.get('metadataavailability','').upper() == 'Y'
        _metadata_flags[db] = m

    return m

def _sourceurl(db):
    '''Return the URL for fetching source objects
    '''

    if db is None:
        db = w.db

    return '{}/{}/sources/{}'.format(w.endpoint, w.lang, db)

def _concepturl(concept, id, db):
    '''Return the URL for fetching source objects
    '''

    if db is None:
        db = w.db

    concept_list = concepts(db)
    if concept_list.get(concept) is None:
        return None

    return '{}/{}/sources/{}/{}/{}'.format(w.endpoint, w.lang, db, concept, id)

