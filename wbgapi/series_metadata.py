
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

    if type(economies) is str:
        if economies == 'all':
            economies = [row['id'] for row in w.economy.list()]
        else:
            economies = [economies]

    if type(time) is str:
        if time == 'all':
            time = [row['id'] for row in w.time.list()]
        else:
            time = [time]

    if db is None:
        db = w.db

    if not w.source.has_metadata(db):
        return None

    for row in w.metadata('sources/{source}/series/{series}/metadata', ['series'], source=db, series=w.queryParam(id, 'series', db=db)):
        if economies:
            row.economies = {}
            # requests for non-existing data throw malformed responses so we must catch for them
            try:
                cs = ';'.join(['{}~{}'.format(elem,row.id) for elem in economies])
                for row2 in w.metadata('sources/{source}/Country-Series/{series}/metadata', ['series'], source=db, series=cs):
                    row.economies[row2.id.split('~')[0]] = row2.metadata['Country-Series']
            except:
                pass

        if time:
            row.time = {}
            try:
                st = ';'.join(['{}~{}'.format(row.id,elem) for elem in time])
                for row2 in w.metdata('sources/{source}/Series-Time/{series}/metadata', ['series'], source=db, series=st):
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
        A Metadata object.  If series/economy or series/time metadata are
        requested they will be stored on the 'economies' and 'time' properties

    Examples:
        print(wbgapi.series.metadata.get('SP.POP.TOTL'))
    '''
    
    for row in fetch(id, economies, time, db):
        return row
