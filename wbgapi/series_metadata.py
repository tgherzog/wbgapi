
'''Access series-level metadata
'''

import wbgapi as w

def fetch(id,economies=[],time=[],db=None):
    '''Return metadata for specified series

    Arguments:
        id:         a series identifier or list-like

        economies:  optional list of economies for which to include series-economy metadata
                    (NB: this is the same metadata returned by economy.metadata.fetch()
                    with the series parameter)

        time:       optional list of time identifiers for which to include series-time metadata

        db:         database; pass None to access the global database

    Returns:
        A generator object which generates Metadata objects. If series/economy or series/time
        metadata are requested they will be stored on the 'economies' and 'time' properties

    Examples:
        for meta = wbgapi.series.metadata.fetch(['SP.POP.TOTL', 'NY.GDP.PCAP.CD']):
            print(meta)
    '''

    pg_size = 50    # large 2-dimensional metadata requests must be paged or the API will barf
                    # this sets the page size. Seems to work well even for very log CETS identifiers

    if type(economies) is str:
        economies = [economies]

    if type(time) is str:
        time = [time]

    if db is None:
        db = w.db

    if not w.source.has_metadata(db):
        return None

    url = 'sources/{}/series/{}/metadata'.format(db, w.queryParam(id))
    for row in w.metadata(url):
        if economies:
            row.economies = {}
            n = 0
            while n < len(economies):
                cs = ';'.join(['{}~{}'.format(elem,row.id) for elem in economies[n:n+pg_size]])
                n += pg_size
                url2 = 'sources/{}/Country-Series/{}/metadata'.format(db, cs)

                # requests for non-existing data throw malformed responses so we must catch for them
                try:
                    for row2 in w.metadata(url2):
                        # w.metadata should be returning single entry dictionaries here since it pages for each new identifier
                        row.economies[row2.id.split('~')[0]] = row2.metadata['Country-Series']
                except:
                    pass

        if time:
            row.time = {}
            n = 0
            while n < len(time):
                st = ';'.join(['{}~{}'.format(row.id,elem) for elem in time[n:n+pg_size]])
                n += pg_size
                url2 = 'sources/{}/Series-Time/{}/metadata'.format(db, st)

                try:
                    for row2 in w.metadata(url2):
                        row.time[row2.id.split('~')[1]] = row2.metadata['Series-Time']
                except:
                    pass

        yield row


def get(id,economies=[],time=[],db=None):
    '''Retrieve a single metadata record

    Arguments:
        id:         a series identifier

        economies:  optional list of economies for which to include series-economy metadata

        time:       optional list of time identifiers for which to include series-time metadata

        db:         database; pass None to access the global database

    Returns:
        A metadadata object.  If series/economy or series/time metadata are
        requested they will be stored on the 'economies' and 'time' properties

    Examples:
        print(wbgapi.series.metadata.get('SP.POP.TOTL'))
    '''
    
    for row in fetch(id, economies, time, db):
        return row
