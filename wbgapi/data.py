
'''Access World Bank API data
'''

import wbgapi as w
try:
    import numpy as np
    import pandas as pd
except ImportError:
    np = None
    pd = None

def fetch(series, economy='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, numericTimeKeys=False, params={}, db=None, **dimensions):
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

    if db is None:
        db = w.db

    concepts = w.source.concepts(db)
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

    url = 'sources/{}'.format(db)
    keys = ['series', 'economy', 'time']
    values = {}
    for k,v in dimensions_.items():
        if k not in concepts:
            raise KeyError('{} is not a concept in database {}'.format(k, db))

        if k not in keys:
            keys.append(k)

        url += '/{}/{}'.format(concepts[k]['key'], '{' + k + '}')
        values[k] = w.queryParam(v, concept=k, db=db)

    aggs = w.economy.aggregates()

    for row in w.refetch(url, keys, params=params_, **values):
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

def FlatFrame(series, economy='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, params={}, db=None, **dimensions):
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

    # we set numericTimeKeys=True so that time values will always be numeric if possible
    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, skipBlanks=skipBlanks, labels=True, numericTimeKeys=True, skipAggs=skipAggs, params=params, db=db, **dimensions):
        if df is None:
            # this assumes that the API returns the same object structure in every row, so we can use the first as a template
            columns = row.keys()
            df = pd.DataFrame(columns=columns)

        df.loc[len(df)] = [row[i][key] if type(row[i]) is dict else row[i] for i in columns]

    return df

def DataFrame(series, economy='all', time='all', index=None, columns=None, mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False, numericTimeKeys=False, timeColumns=False, params={}, db=None, **dimensions):
    '''Retrieve a 2-dimensional pandas dataframe. 
    
    Arguments:
        series:             a series identifier or list-like, e.g., SP.POP.TOTL

        economy:            an economy identifier or list-like, e.g., 'BRA' or ['USA', 'CAN', 'MEX']

        time:               a time identifier or list-like, e.g., 'YR2015' or range(2010,2020).
                            Both element keys and values are acceptable

        index:              name or list of dimensions for the DataFrame's index, e.g., 'economy'. If None then the function
                            will define the index based on your request. Note: to get a dataframe with no index
                            (i.e., 0-based integers) call `reset_index()` with on the return value of this function.

        columns:            name of the dimension for the DataFrame's columns, e.g., 'series'. If None then the function
                            will define columns based on your request.

        mrv:                return only the specified number of most recent values (same time period for all economies)

        mrnev:              return only the specified number of non-empty most recent values (time period varies)

        skipBlanks:         skip empty observations

        labels:             include the dimension name for rows

        skipAggs:           skip aggregates

        numericTimeKeys:    store the time object by value (e.g., 2014) instead of key ('YR2014') if value is numeric

        timeColumns:        add extra columns to show the time dimension for each series/economy
                            If 'auto' then the function will guess based on other parameters

        params:             extra query parameters to pass to the API

        dimensions:         extra dimensions, database specific (e.g., version)
        
    Returns:
        a pandas DataFrame

    Examples:
        # 5 years of population data (with economy names)
        wbgapi.data.DataFrame('SP.POP.TOTL', time=range(2010,2020),labels=True)

        # Most recent poverty and income data for LAC
        wbgapi.data.DataFrame(['SI.POV.NAHC', 'NY.GDP.PCAP.CD'], economy=wb.region.members('LAC'),mrnev=1,timeColumns=True)

        # Fetch most recent CO2 emissions for each country and merge its income group
        wbgapi.data.DataFrame('EN.ATM.CO2E.PC',mrnev=1).join(wbgapi.economy.DataFrame()['incomeLevel'])

        # Top 10 emitters per capita
        wbgapi.data.DataFrame('EN.ATM.CO2E.PC',mrnev=1,labels=True).sort_values('EN.ATM.CO2E.PC',ascending=False).head(10)

    Notes:
        timeColumns currently defaults to False so that the default column composition is consistent. This may change to 'auto'
        at some point, so that mrv behavior is more intuitive for data discovery
    '''

    def frame(index):

        if len(index) > 1:
            i = [[]] * len(index)
            return pd.DataFrame(index=pd.MultiIndex(levels=i, codes=i, names=tuple(index)))

        df = pd.DataFrame()
        df.index.name = index[0]
        return df

    def is_single(x):

        if type(x) is str:
            if x == 'all':
                return False
            elif x == 'mrv':
                return True

        # not necessary to pass db since we don't actually care about the parameters just the count of them
        return len(w.queryParam(x).split(';')) == 1

    if pd is None:
        raise ModuleNotFoundError('you must install pandas to use this feature')

    # set up the axes by looking at the index/column parameters
    concepts = ['economy','series','time']
    for k,v in w.source.concepts(db).items():
        if k not in concepts:
            concepts.insert(0, k)

    if type(index) is str:
        index = [index]

    if index is None or columns is None:
        # we need to infer at least one dimension

        dimensions_ = {'series': series, 'economy': economy, 'time': time}
        dimensions_.update(dimensions)

        axes = concepts.copy()

        # now we reduce axes by eliminating any dimension consisting of 
        # one element not defined in the calling parameters, with a stop
        # if we reduce to 2 dimensions
        x = concepts.copy()
        x.reverse()
        for k in x:
            if len(axes) == 2:
                break

            if k == columns or (type(index) is list and k in index):
                continue

            values = dimensions_.get(k, 'all')
            if k == 'time' and (mrv == 1 or mrnev == 1 or is_single(values)):
                axes.remove(k)
                if timeColumns == 'auto' and (mrv == 1 or mrnev == 1):
                    timeColumns = True

            elif is_single(values):
                axes.remove(k)

        if columns is None and index is None:
            columns = axes.pop(-1)
            index = axes
        elif columns is None:
            # try to guess a column based on what index doesn't define
            x = list(filter(lambda x: x not in index, axes))
            if len(x) > 0:
                columns = x[-1]
            elif (set(concepts) - set(list)) > 0:
                # index has claimed all non-singular dimensions, so set columns from the full concepts list
                x = list(filter(lambda x: x not in index, concepts))
                columns = x[-1]
            else:
                # index is the same as the concepts list. That's not allowed
                raise ValueError('one dimension must be a column')

        elif index is None:
            axes.remove(columns)
            index = axes

    # sanity checks
    if type(columns) is not str or columns not in concepts:
        raise ValueError('columns must be None or a dimension')

    if type(index) is not list or len(set(index) - set(concepts)) > 0:
        raise ValueError('index must be None or a dimension list')

    if columns in index:
        raise ValueError('columns cannot be an element in index')

    if columns == 'time' or 'time' in index or timeColumns == 'auto':
        timeColumns = False

    # for now let's see if it works to build the dataframe dynamically
    df = frame(index)
    dummy = pd.Series()    # empty series - never assigned actual values
    ts_suffix = ':T'
    concepts = w.source.concepts(db)
    if labels:
        # create a separate dataframe for labels so that we can control the column position below
        df2 = frame(index)

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, skipBlanks=skipBlanks, labels=True, skipAggs=skipAggs, numericTimeKeys=numericTimeKeys, params=params, db=db, **dimensions):
        column_key = row[columns]['id']
        if len(index) == 1:
            index_key = row[index[0]]['id']
        else:
            index_key = tuple(map(lambda x: row[x]['id'], index))

        # this logic only assigns values to locations that don't yet exist. First observations thus take precedent over subsequent ones
        if pd.isna(df.get(column_key, dummy).get(index_key)):
            df.loc[index_key, column_key] = np.nan if row['value'] is None else row['value']
            if timeColumns:
                df.loc[index_key, column_key + ts_suffix] = row['time']['value']

            if labels:
                for i in index:
                    df2.loc[index_key, concepts[i]['value']] = row[i]['value']
        
    df.sort_index(axis=0,inplace=True)
    df.sort_index(axis=1,inplace=True)
    if labels:
        return df2.join(df)
        # return pd.concat([df2,df], axis=1, sort=False)
        
    return df
        

def get(series, economy, time='all', mrv=None, mrnev=None, labels=False, numericTimeKeys=False, db=None, **dimensions):
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

    for row in fetch(series, economy, time, mrv=mrv, mrnev=mrnev, labels=labels, numericTimeKeys=numericTimeKeys, params={'per_page': 1}, db=db, **dimensions):
        return row

def footnote(series, economy, time, db=None):
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

    if db is None:
        db = w.db

    # note that this only supports singular footnote references at this point, although the interface suggests otherwise
    url = 'sources/{source}/footnote/{economy}~{series}~{time}/metadata'
    try:
        for row in w.metadata(url, ['series'], source=db, series=series, economy=economy, time=w.queryParam(time, 'time', db=db)):
            return row.metadata['FootNote']
    except:
        pass    # will return None then

