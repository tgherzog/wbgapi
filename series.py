
import wbgapi as w

_economyDimensions = {}

def list():
    '''Iterate over the list of indicators/series in the current database

    Returns:
        a generator object

    Example:
        for elem in wbgapi.series.list():
            print elem['id'], elem['name']

    '''
    return w.source.features('series')

def get(series, countries='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False):
    '''Retrieve API data for the current database
    Parameters:
        series: (required) the series identifier, e.g., SP.POP.TOTL

        countries: country code to select. default=all

        time: time period to select. default=all

        mrv:  return only the specified number of most recent values (same time period for all countries)

        mrnev: return only the specified number of non-empty most recent values (time period varies per country)

        skipBlanks:  set to True to skip empty observations

        labels: set to True to include both dimension id and name (e.g., ZWE & Zimbabwe, not just ZWE)

        skipAggs:    set to True to skip aggregates (return only countries)

    Notes:
        series, countries and time can be either scalar strings ('SP.POP.TOTL', 'BRA')
        or arrays (['SP.POP.TOTL', 'NY.GDP.PCAP.CD'], ['BRA', 'ARG'])

    Returns:
        A generator object

    Examples:
        # print name and population of all countries
        for elem in wbgapi.series.get('SP.POP.TOTL',labels=True):
            print elem['country']['value'], elem['time']['value'], elem['value']

        # dict of most recent population data for countries over 100000
        popData = {elem['country']: elem['value'] for elem in wbgapi.series.get('SP.POP.TOTL', mrnev=1, skipAggs=True) if elem['value'] > 100000}
        
    '''

    params = {}
    if mrv:
        params['mrv'] = mrv
    elif mrnev:
        params['mrnev'] = mrnev

    if skipAggs:
        aggs = w.agg_list()

    economy_dimension_label = _economyDimension(w.db)
    url = '{}/{}/sources/{}/series/{}/{}/{}/time/{}'.format(w.endpoint, w.lang, w.db, w._apiParam(series), economy_dimension_label, w._apiParam(countries), w._apiParam(time))
    for row in w.fetch(url, params):
        if skipBlanks and row['value'] is None:
            continue

        skip = False

        x = {'value': row['value']}
        for elem in row['variable']:
            key = elem['concept'].lower()
            if key == economy_dimension_label:
                key = w.economy_key
                if skipAggs and elem['id'] in aggs:
                    skip = True
                    break

            if labels:
                del(elem['concept'])
                x[key] = elem
            else:
                x[key] = elem['id']

        if not skip:
            yield x

def _economyDimension(db):
    '''Helper function to discern the API name of the economy dimension. This varies by database
    '''

    global _economyDimensions

    t = _economyDimensions.get(db)
    if t is None:
        concepts = w.source.concepts(db).keys()
        for elem in ['country', 'economy', 'admin%20region', 'states', 'provinces']:
            if elem in concepts:
                t = elem
                _economyDimensions[db] = t
                break

    return t
