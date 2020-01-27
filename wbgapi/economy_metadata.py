
'''Access economy-level metadata
'''

import wbgapi as w

def fetch(id,series=[],db=None):
    '''Return metadata for the specified economy

    Arguments:
        id:         an economy identifier or list-like

        series:     optional list of series for which to include series-economy metadata
                    (NB: this is the same metadata returned by series.metadata.fetch() with
                    the economies parameter)

        db:         database; pass None to access the global database

    Returns:
        a generator which generates Metadata objects. If series/economy metadata
        is requested it will be stored on the 'series' property of the object.

    Notes:
        Passing a large series list will be very resource intense and inefficient. It might be
        better to call series.metadata.fetch() with a relatively small list of countries

    Example:
        for meta = wbgapi.economy.metadata.fetch(['COL', 'BRA']):
            print(meta)
        
    '''

    pg_size = 50    # large 2-dimensional metadata requests must be paged or the API will barf
                    # this sets the page size. Seems to work well even for very log CETS identifiers

    if db is None:
        db = w.db

    if not w.source.has_metadata(db):
        return None

    if type(series) is str:
        series = [series]

    url = 'sources/{}/country/{}/metadata'.format(db, w.queryParam(id, 'economy'))
    for row in w.metadata(url):
        if series:
            row.series = {}
            n = 0
            while n < len(series):
                cs = ';'.join(['{}~{}'.format(row.id,elem) for elem in series[n:n+pg_size]])
                n += pg_size
                url2 = 'sources/{}/Country-Series/{}/metadata'.format(db, cs)

                # requests for non-existing data throw malformed responses so we must catch for them
                try:
                    for row2 in w.metadata(url2):
                        # w.metadata should be returning single entry dictionaries here since it pages for each new identifier
                        row.series[row2.id.split('~')[1]] = row2.metadata['Country-Series']
                except:
                    pass

        yield row


def get(id,series=[], db=None):
    '''Retrieve a single metadata record

    Arguments:
        id:         an economy identifier or list-like

        series:     optional list of series for which to include series-country metadata

        db:         database; pass None to access the global database

    Returns:
        A metadata object. If series/economy metadata is requested it will be stored on the
        'series' property of the object.

    Example:
        print(wbgapi.economy.metadata.get('COL'))
    '''
    
    for row in fetch(id, series, db):
        return row
