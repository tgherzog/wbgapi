
import wbgapi as w

def fetch(series, countries='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, params={}):
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
        for elem in wbgapi.data.fetch('SP.POP.TOTL',labels=True):
            print elem['country']['value'], elem['time']['value'], elem['value']

        # dict of most recent population data for countries over 100000
        popData = {elem['country']: elem['value'] for elem in wbgapi.data.fetch('SP.POP.TOTL', mrnev=1, skipAggs=True) if elem['value'] > 100000}
        
    '''

    (url, params_, economy_dimension_label) = _request(series, countries, time, mrv, mrnev, params)
    aggs = w.economy.aggregates()

    url = '{}/{}/sources/{}/series/{}/{}/{}/time/{}'.format(w.endpoint, w.lang, w.db, w.queryParam(series), economy_dimension_label, w.queryParam(countries), w.queryParam(time))
    for row in w.fetch(url, params_):
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

            if not skip:
                if labels:
                    del(elem['concept'])
                    x[key] = elem
                    if key == w.economy_key:
                        x[key]['aggregate'] = elem['id'] in aggs
                else:
                    x[key] = elem['id']
                    if key == w.economy_key:
                        x['aggregate'] = elem['id'] in aggs

        if not skip:
            yield x

def get(series, countries, time='all', mrv=None, mrnev=None, labels=False):

    for row in fetch(series, countries, time, mrv=mrv, mrnev=mrnev, labels=labels, params={'per_page': 1}):
        return row

def footnote(series, country, time):

    url = '{}/{}/sources/{}/footnote/{}~{}~{}/metadata'.format(w.endpoint, w.lang, w.db, country, series, time)
    try:
        for row in w.metadata(url):
            return row.metadata['FootNote']
    except:
        raise


def _request(series, countries='all', time='all', mrv=None, mrnev=None, params={}):
    '''Return the URL and parameters for data requests
    '''

    params_ = {}
    params_.update(params)
    if mrv:
        params_['mrv'] = mrv
    elif mrnev:
        params_['mrnev'] = mrnev

    economy_dimension_label = w.economy.dimension_name()
    url = '{}/{}/sources/{}/series/{}/{}/{}/time/{}'.format(w.endpoint, w.lang, w.db, w.queryParam(series), economy_dimension_label, w.queryParam(countries), w.queryParam(time))
    return (url, params_, economy_dimension_label)
