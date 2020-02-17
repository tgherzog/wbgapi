
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

    if db is None:
        db = w.db

    if not w.source.has_metadata(db):
        return None

    if type(series) is str:
        if series == 'all':
            # could be huge
            series = [row['id'] for row in w.series.list()]
        else:
            series = [series]

    # as far as I can tell even for databases where the dimension is called 'economy' or something else the metadata API still 
    # wants 'country' as a parameter
    for row in w.metadata('sources/{source}/country/{economy}/metadata', ['economy'], source=db, economy=w.queryParam(id, 'economy', db=db)):
        if series:
            row.series = {}
            # requests for non-existing data throw malformed responses so we must catch for them
            try:
                cs = ';'.join(['{}~{}'.format(row.id,elem) for elem in series[n:n+pg_size]])
                for row2 in w.metadata('sources/{source}/Country-Series/{series}/metadata', ['series'], source=db, series=cs):
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
