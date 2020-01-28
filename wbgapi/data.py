
'''Access World Bank API data
'''

import wbgapi as w
try:
    import numpy as np
    import pandas as pd
except ImportError:
    np = None
    pd = None

def fetch(series, economy='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, numericTimeKeys=False, params={}, **dimensions):
    '''Retrieve rows of data for the current database

    Arguments:
        series:             a series identifier or list-like, e.g., SP.POP.TOTL

        economy:            an economy identifier or list-like, e.g., 'BRA' or ['USA', 'CAN', 'MEX']

        time:               a time identifier or list-like, e.g., 'YR2015' or range(2010,2020).
                            Both element keys and values are acceptable

        mrv:                return only the specified number of most recent values (same time period for all economies)

        mrnev:              return only the specified number of non-empty most recent values (time period varies)

        skipBlanks:         skip empty observations

        labels:             include both dimension id and name (e.g., ZWE & Zimbabwe, not just ZWE)

        skipAggs:           skip aggregates

        numericTimeKeys:    store the time object by value (e.g., 2014) instead of key ('YR2014') if value is numeric

        params:             extra query parameters to pass to the API

        dimensions:         extra dimensions, database specific (e.g., version)

    Returns:
        A generator object

    Examples:
        # print name and population of all economies for all available years
        for elem in wbgapi.data.fetch('SP.POP.TOTL',labels=True):
            print(elem['economy']['value'], elem['time']['value'], elem['value'])

        # fetch data for Brazil for odd-numbered years
        for elem in wbgapi.data.fetch('NY.GDP.PCAP.CD', 'BRA', range(2011,2020,2)):
            print(elem['value'])

        # most recent poverty rates for all LAC countries
        for elem in wbgapi.data.fetch('SI.POV.NAHC', economy=wb.region.members('LAC'), mrnev=1):
            print(elem['economy'], elem['time'], elem['value'])

        # dict of most recent population data for economies over 100000
        popData = {i['economy']: i['value'] for i in wbgapi.data.fetch('SP.POP.TOTL', mrnev=1, skipAggs=True) if i['value'] > 100000}
        
    '''

    concepts = w.source.concepts(w.db)
    concept_keys = {v['key']: k for k,v in concepts.items()}
    params_ = {}
    params_.update(params)
    if mrv:
        params_['mrv'] = mrv
    elif mrnev:
        params_['mrnev'] = mrnev

    # you can thus pass series, economy, and time in the dimensions array, and those will overwrite the explicit parameters
    dimensions_ = {'series': series, 'economy': economy, 'time': time}
    dimensions_.update(dimensions)

    url = 'sources/{}'.format(w.db)
    for k,v in dimensions_.items():
        if k not in concepts:
            raise KeyError('{} is not a concept in database {}'.format(k, w.db))

        url += '/{}/{}'.format(concepts[k]['key'], w.queryParam(v, concept=k))

    aggs = w.economy.aggregates()

    for row in w.fetch(url, params_):
        if skipBlanks and row['value'] is None:
            continue

        skip = False

        x = {'value': row['value']}
        for elem in row['variable']:
            key = concept_keys[elem['concept'].lower()]
            if key == 'economy' and skipAggs and elem['id'] in aggs:
                skip = True
                break

            if not skip:
                if labels:
                    del(elem['concept'])
                    x[key] = elem
                    if key == 'economy':
                        x[key]['aggregate'] = elem['id'] in aggs
                    elif key == 'time' and numericTimeKeys and elem['value'].isdigit():
                        x[key]['id'] = int(elem['value'])
                else:
                    x[key] = elem['id']
                    if key == 'economy':
                        x['aggregate'] = elem['id'] in aggs
                    elif key == 'time' and numericTimeKeys and elem['value'].isdigit():
                        x[key] = int(elem['value'])

        if not skip:
            yield x

def FlatFrame(series, economy='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, params={}, **dimensions):
    '''Retrieve a flat pandas dataframe (1 row per observation)

    Arguments:
        series:             a series identifier or list-like, e.g., SP.POP.TOTL

        economy:            an economy identifier or list-like, e.g., 'BRA' or ['USA', 'CAN', 'MEX']

        time:               a time identifier or list-like, e.g., 'YR2015' or range(2010,2020).
                            Both element keys and values are acceptable

        mrv:                return only the specified number of most recent values (same time period for all economies)

        mrnev:              return only the specified number of non-empty most recent values (time period varies)

        skipBlanks:         skip empty observations

        labels:             return the dimension name instead of the identifier

        skipAggs:           skip aggregates

        params:             extra query parameters to pass to the API

        dimensions:         extra dimensions, database specific (e.g., version)
        
    Returns:
        a pandas DataFrame

    Notes:
        values in the time column are numeric if possible (2015 not 'YR2015')
    '''

    if pd is None:
        raise ModuleNotFoundError('you must install pandas to use this feature')

    key = 'value' if labels else 'id'
    df = None

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, skipBlanks=skipBlanks, labels=True, numericTimeKeys=True, skipAggs=skipAggs, params=params, **dimensions):
        if df is None:
            # this assumes that the API returns the same object structure in every row, so we can use the first as a template
            columns = row.keys()
            df = pd.DataFrame(columns=columns)
            keys = {i: 'id' if i == 'time' else key for i in columns}

        df.loc[len(df)] = [row[i][keys[i]] if type(row[i]) is dict else row[i] for i in columns]

    return df

def DataFrame(series, economy='all', time='all', axes='auto', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, flat=False, numericTimeKeys=False, timeColumns=False, params={}):
    '''Retrieve a 2-dimensional pandas dataframe. 
    
    Arguments:
        series:             a series identifier or list-like, e.g., SP.POP.TOTL

        economy:            an economy identifier or list-like, e.g., 'BRA' or ['USA', 'CAN', 'MEX']

        time:               a time identifier or list-like, e.g., 'YR2015' or range(2010,2020).
                            Both element keys and values are acceptable

        axes:               a 2-element array specifiying the dimensions to use for the index (row) and column
                            of the dataframe. If 'auto' then the function will choose for you based on your
                            request. This works best if at least one of series, economies or time is restricted
                            to a single value (mrv=1 and mrnev=1 effectively do the same thing).

        mrv:                return only the specified number of most recent values (same time period for all economies)

        mrnev:              return only the specified number of non-empty most recent values (time period varies)

        skipBlanks:         skip empty observations

        labels:             include the dimension name for rows

        skipAggs:           skip aggregates

        flat:               same as calling FlatFrame()

        numericTimeKeys:    store the time object by value (e.g., 2014) instead of key ('YR2014') if value is numeric

        timeColumns:        add extra columns to show the time dimension for each series/economy

        params:             extra query parameters to pass to the API
        
    Returns:
        a pandas DataFrame

    Examples:
        # 5 years of population data (with economy names)
        wbgapi.data.DataFrame('SP.POP.TOTL, time=range(2010,2020),labels=True)

        # Most recent poverty and income data for LAC
        wbgapi.data.DataFrame(['SI.POV.NAHC', 'NY.GDP.PCAP.CD'], economy=wb.region.members('LAC'),mrnev=1,timeColumns=True)

        # Fetch most recent CO2 emissions for each country and merge its income group
        wbgapi.data.DataFrame('EN.ATM.CO2E.PC',mrnev=1).join(wbgapi.economy.DataFrame()['incomeLevel'])

        # Top 10 emitters per capita
        wbgapi.data.DataFrame('EN.ATM.CO2E.PC',mrnev=1,labels=True).sort_values('EN.ATM.CO2E.PC',ascending=False).head(10)
    '''

    if flat:
        return FlatFrame(series, economy, time, mrv=mrv, mrnev=mrnev, skipBlanks=skipBlanks, labels=labels, skipAggs=skipAggs, params=params)

    if pd is None:
        raise ModuleNotFoundError('you must install pandas to use this feature')

    if type(axes) is str and axes == 'auto':
        axes = ['economy', 'series', 'time']
        if mrv == 1 or mrnev == 1 or (time != 'all' and len(w.queryParam(time, 'time').split(';')) == 1):
            axes.remove('time')
        elif len(w.queryParam(series, 'series').split(';')) == 1:
            axes.remove('series')
        elif economy != 'all' and len(w.queryParam(economy, 'economy').split(';')) == 1:
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
    ts_suffix = ':T'
    if labels:
        # create a separate dataframe for labels so that we can control the column position below
        df2 = pd.DataFrame()

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, skipBlanks=skipBlanks, labels=True, skipAggs=skipAggs, numericTimeKeys=numericTimeKeys, params=params):
        # this logic only assigns values to locations that don't yet exist. First observations thus take precedent over subsequent ones
        if pd.isna(df.get(row[axes[1]]['id'], dummy).get(row[axes[0]]['id'])):
            column_key = row[axes[1]]['id']
            index_key  = row[axes[0]]['id']
            df.loc[index_key, column_key] = np.nan if row['value'] is None else row['value']
            if timeColumns:
                df.loc[index_key, column_key + ts_suffix] = row['time']['value']

            if labels:
                df2.loc[index_key, 'Label'] = row[axes[0]]['value']
        
    df.sort_index(axis=0,inplace=True)
    df.sort_index(axis=1,inplace=True)
    if labels:
        return pd.concat([df2,df], axis=1,sort=True)
        
    return df
        

def get(series, economy, time='all', mrv=None, mrnev=None, labels=False, numericTimeKeys=False, **dimensions):
    '''Retrieve a single data point for the current database

    Arguments:
        series:             a series identifier

        economy:            an economy identifier

        time:               a time identifier.  Both element keys and values are acceptable

        mrv:                return only the specified number of most recent values (same time period for all economies)

        mrnev:              return only the specified number of non-empty most recent values (time period varies)

        labels:             include both dimension id and name (e.g., ZWE & Zimbabwe, not just ZWE)

        numericTimeKeys:    store the time object by value (e.g., 2014) instead of key ('YR2014') if value is numeric

        dimensions:         extra dimensions, database specific (e.g., version)

    Returns:
        a data observation

    Notes:
        This function simply calls fetch() and returns the first result. Hence, you should set mrv or mrnev to 1, or set
        time to a single value to get predictable results.

    Example:
        # print the last population estimate for France
        print(wbgapi.data.get('SP.POP.TOTL', 'FRA', mrnev=1)['value'])
    '''

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, labels=labels, numericTimeKeys=numericTimeKeys, params={'per_page': 1}, **dimensions):
        return row

def footnote(series, economy, time):
    '''Return the footnote for a single data point, if any

    Arguments:
        series:             a series identifier

        economy:            an economy identifier

        time:               a time identifier.  Both element keys and values are acceptable

    Returns:
        footnote text, or None

    Example:
        print(wbgapi.data.footnote('SP.POP.TOTL', 'FRA', 2015))
    '''

    url = 'sources/{}/footnote/{}~{}~{}/metadata'.format(w.db, economy, series, w.queryParam(time, 'time'))
    try:
        for row in w.metadata(url):
            return row.metadata['FootNote']
    except:
        pass    # will return None then

