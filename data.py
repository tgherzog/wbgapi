
import wbgapi as w
try:
    import pandas as pd
except ImportError:
    pd = None

def fetch(series, economy='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, params={}):
    '''Retrieve API data for the current database
    Parameters:
        series: (required) the series identifier, e.g., SP.POP.TOTL

        economy: country code to select. default=all

        time: time period to select. default=all

        mrv:  return only the specified number of most recent values (same time period for all economies)

        mrnev: return only the specified number of non-empty most recent values (time period varies per country)

        skipBlanks:  set to True to skip empty observations

        labels: set to True to include both dimension id and name (e.g., ZWE & Zimbabwe, not just ZWE)

        skipAggs:    set to True to skip aggregates (return only countries)

    Notes:
        series, economy and time can be either scalar strings ('SP.POP.TOTL', 'BRA')
        or arrays (['SP.POP.TOTL', 'NY.GDP.PCAP.CD'], ['BRA', 'ARG'])

    Returns:
        A generator object

    Examples:
        # print name and population of all economies
        for elem in wbgapi.data.fetch('SP.POP.TOTL',labels=True):
            print elem['economy']['value'], elem['time']['value'], elem['value']

        # dict of most recent population data for economies over 100000
        popData = {elem['economy']: elem['value'] for elem in wbgapi.data.fetch('SP.POP.TOTL', mrnev=1, skipAggs=True) if elem['value'] > 100000}
        
    '''

    (url, params_, economy_dimension_label) = _request(series, economy, time, mrv, mrnev, params)
    aggs = w.economy.aggregates()

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

def DataFrame(series, economy='all', time='all', axes='auto', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, params={}):

    if pd is None:
        raise ModuleNotFoundError('you must install pandas to use this feature')

    if type(axes) is str and axes == 'auto':
        axes = ['economy', 'series', 'time']
        if mrv == 1 or mrnev == 1 or (time != 'all' and len(w.queryParam(time).split(';')) == 1):
            axes.remove('time')
        elif len(w.queryParam(series).split(';')) == 1:
            axes.remove('series')
        elif economy != 'all' and len(w.queryParam(economy).split(';')) == 1:
            axes.remove('economy')
        else:
            del(axes[2])

    t = set(axes)
    if len(t) != 2 or t - set(['economy', 'series', 'time']):
        raise ValueError('axes must be \'auto\' or exactly 2 of economy, series, time')

    # for now let's see if it works to build the dataframe dynamically
    df = pd.DataFrame()
    key = 'value' if labels else 'id'

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, skipBlanks=skipBlanks, labels=True, skipAggs=skipAggs, params=params):
        df.loc[row[axes[0]][key], row[axes[1]][key]] = row['value']
        
    df.sort_index(axis=0,inplace=True)
    df.sort_index(axis=1,inplace=True)
    return df
        
        

def get(series, economy, time='all', mrv=None, mrnev=None, labels=False):

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, labels=labels, params={'per_page': 1}):
        return row

def footnote(series, economy, time):

    url = '{}/{}/sources/{}/footnote/{}~{}~{}/metadata'.format(w.endpoint, w.lang, w.db, economy, series, time)
    try:
        for row in w.metadata(url):
            return row.metadata['FootNote']
    except:
        raise


def _request(series, economy='all', time='all', mrv=None, mrnev=None, params={}):
    '''Return the URL and parameters for data requests
    '''

    params_ = {}
    params_.update(params)
    if mrv:
        params_['mrv'] = mrv
    elif mrnev:
        params_['mrnev'] = mrnev

    economy_dimension_label = w.economy.dimension_name()
    url = '{}/{}/sources/{}/series/{}/{}/{}/time/{}'.format(w.endpoint, w.lang, w.db, w.queryParam(series), economy_dimension_label, w.queryParam(economy), w.queryParam(time))
    return (url, params_, economy_dimension_label)
