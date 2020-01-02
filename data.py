
import wbgapi as w
try:
    import pandas as pd
except ImportError:
    pd = None

def fetch(series, economy='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, numericTimeKeys=False, params={}):
    '''Retrieve API data for the current database
    Arguments:
        series: (required) the series identifier, e.g., SP.POP.TOTL

        economy: country code to select. default=all

        time: time period to select. default=all

        mrv:  return only the specified number of most recent values (same time period for all economies)

        mrnev: return only the specified number of non-empty most recent values (time period varies per country)

        skipBlanks:  set to True to skip empty observations

        labels: set to True to include both dimension id and name (e.g., ZWE & Zimbabwe, not just ZWE)

        skipAggs:    set to True to skip aggregates (return only economies)

        numericTimeKeys:   store the time object by value (e.g., 2014) instead of key ('YR2014') if value is numeric

        params:             extra query parameters to pass to the API

    Notes:
        series, economy and time can be either scalar strings ('SP.POP.TOTL', 'BRA')
        or array-like objects (['SP.POP.TOTL', 'NY.GDP.PCAP.CD'], ['BRA', 'ARG'])

        time values can be either keys (e.g., 'YR2014') or values (2014)

    Returns:
        A generator object

    Examples:
        # print name and population of all economies
        for elem in wbgapi.data.fetch('SP.POP.TOTL',labels=True):
            print elem['economy']['value'], elem['time']['value'], elem['value']

        # fetch data for Brazil for odd-numbered years
        for elem in wbgapi.data.fetch('NY.GDP.PCAP.CD', 'BRA', range(2011,2020,2)):
            print elem['value']

        # dict of most recent population data for economies over 100000
        popData = {elem['economy']: elem['value'] for elem in wbgapi.data.fetch('SP.POP.TOTL', mrnev=1, skipAggs=True) if elem['value'] > 100000}
        
    '''

    (url, params_, economy_dimension_label, time_dimension_label) = _request(series, economy, time, mrv, mrnev, params)
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
            elif key == time_dimension_label:
                key = w.time_key

            if not skip:
                if labels:
                    del(elem['concept'])
                    x[key] = elem
                    if key == w.economy_key:
                        x[key]['aggregate'] = elem['id'] in aggs
                    elif key == w.time_key and numericTimeKeys and elem['value'].isdigit():
                        x[key]['id'] = int(elem['value'])
                else:
                    x[key] = elem['id']
                    if key == w.economy_key:
                        x['aggregate'] = elem['id'] in aggs
                    elif key == w.time_key and numericTimeKeys and elem['value'].isdigit():
                        x[key] = int(elem['value'])

        if not skip:
            yield x

def DataFrame(series, economy='all', time='all', axes='auto', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, numericTimeKeys=False, timeColumns=False, params={}):
    '''Retrieve a 2-dimensional pandas dataframe. 
    
    Arguments:
        series: (required) the series identifier, e.g., SP.POP.TOTL

        economy: country code to select. default=all

        time: time period to select. default=all

        axes: a 2-element array specifying the index (row) and column of the dataframe. If 'auto' then
              the function will choose these for you based on other parameters. This can give somewhat
              unpredicatable results if multiple series, economies and time periods are passed
        
        mrv:  return only the specified number of most recent values (same time period for all economies)

        mrnev: return only the specified number of non-empty most recent values (time period varies per country)

        skipBlanks:  set to True to skip empty observations

        labels:     include the dimension name for rows

        slipAggs:   skip aggregates (return only economies)

        numericTimeKeys:   store the time object by value (e.g., 2014) instead of key ('YR2014') if value is numeric

        timeColumns:        add extra columns to show the time dimension for each series/economy

        params:             extra query parameters to pass to the API
        
    '''

    if pd is None:
        raise ModuleNotFoundError('you must install pandas to use this feature')

    if type(axes) is str and axes == 'auto':
        axes = ['economy', 'series', 'time']
        if mrv == 1 or mrnev == 1 or (time != 'all' and len(w.time.queryParam(time).split(';')) == 1):
            axes.remove('time')
        elif len(w.series.queryParam(series).split(';')) == 1:
            axes.remove('series')
        elif economy != 'all' and len(w.economy.queryParam(economy).split(';')) == 1:
            axes.remove('economy')
        else:
            del(axes[2])

    t = set(axes)
    if len(t) != 2 or t - set(['economy', 'series', 'time']):
        raise ValueError('axes must be \'auto\' or exactly 2 of economy, series, time')

    # sanity check: don't include time column if it's a dimension
    if 'time' in axes:
        timeColumns = False

    # for now let's see if it works to build the dataframe dynamically
    df = pd.DataFrame()
    dummy = pd.Series()    # empty series - never assigned actual values
    if labels:
        # create a separate dataframe for labels so that we can control the column position below
        df2 = pd.DataFrame()

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, skipBlanks=skipBlanks, labels=True, skipAggs=skipAggs, numericTimeKeys=numericTimeKeys, params=params):
        # this logic only assigns values to locations that don't yet exist. First observations thus take precedent over subsequent ones
        if pd.isna(df.get(row[axes[1]]['id'], dummy).get(row[axes[0]]['id'])):
            df.loc[row[axes[0]]['id'], row[axes[1]]['id']] = row['value']
            if timeColumns:
                df.loc[row[axes[0]]['id'], row[axes[1]]['id'] + ':T'] = row['time']['value']

            if labels:
                df2.loc[row[axes[0]]['id'], 'Label'] = row[axes[0]]['value']
        
    df.sort_index(axis=0,inplace=True)
    df.sort_index(axis=1,inplace=True)
    if labels:
        return pd.concat([df2,df], axis=1,sort=True)
        
    return df
        

def get(series, economy, time='all', mrv=None, mrnev=None, labels=False, numericTimeKeys=False):

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, labels=labels, numericTimeKeys=numericTimeKeys, params={'per_page': 1}):
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
    time_dimension_label = w.time.dimension_name()
    url = '{}/{}/sources/{}/series/{}/{}/{}/{}/{}'.format(w.endpoint, w.lang, w.db, w.series.queryParam(series), economy_dimension_label, w.economy.queryParam(economy), time_dimension_label, w.time.queryParam(time))
    return (url, params_, economy_dimension_label, time_dimension_label)
