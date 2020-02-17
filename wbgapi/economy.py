
'''Access information about the economies in a database.

Economies can include countries, aggregates, and sub-national regions. The
economy dimension in a World Bank database can go by various concept names,
but the wbgapi module tries to insulate the user from most of these
inconsistencies.

Each database in the World Bank API has its own list of economies. However,
databases that are country-based share a common set of classifications for regions,
income and lending groups. The wbgapi tries to integrate these by including
classifications in economy records where possible. Obviously these won't apply
to databases that don't adhere to the country-level coding standards.
'''

import wbgapi as w
from . import economy_metadata as metadata
from .economy_coder import coder, coder_report
from functools import reduce
import builtins
try:
    import numpy as np
    import pandas as pd
except ImportError:
    np = None
    pd = None

_aggs = None

# a dict of ISO2 code equivalents, if we ever need this
_iso2Codes = {}

# dictionary of region, admin, lendingType and incomeLevel classifications per country. Also lon and lat
_class_data = None

# translated names of regions and cities. This is keyed by language and code
_localized_metadata = {}

def list(id='all',labels=False,skipAggs=False, db=None):
    '''Return a list of economies in the current database

    Arguments:
        id:         an economy identifier or list-like

        skipAggs:   skip aggregates

    Returns:
        a generator object

    Example:
        for elem in wbgapi.economy.list():
            print(elem['id'], elem[' value'])

    '''
    global _class_data

    update_caches()
    for row in w.source.features('economy', w.queryParam(id, 'economy', db=db), db=db):
        _build(row,labels)
        if skipAggs == False or row['aggregate'] == False:
            yield row

def get(id,labels=False, db=None):
    '''Retrieve the specified economy

    Arguments:
        id:     an economy ID

    Returns:
        a database object

    Example:
        print(wbgapi.economy.get('BRA')['value'])
    '''

    update_caches()
    row = w.source.feature('economy', id, db=db)
    _build(row,labels)
    return row

    
def _build(row,labels=False):
    '''utility function to build an economy record from API and cached data
    '''

    global _class_data, _localized_metadata

    cd = _class_data.get(row['id'])
    if cd is None:
        cd = _class_data.get('___')
    if cd:
        row.update(cd)
        row['capitalCity'] = _localized_metadata[w.lang].get('capitalCity:'+row['id'],'')
        if labels:
            for key in ['region', 'adminregion', 'lendingType', 'incomeLevel']:
                row[key] = {'id': row[key], 'value': _localized_metadata[w.lang].get(row[key],'')}


def DataFrame(id='all',labels=False, skipAggs=False, db=None):
    '''Return a pandas DataFrame of economy records

    Arguments:
        id:         an economy identifier or list-like

        labels:     return classification names instead of their 3-character identifier codes

        skipAggs:   skip aggregates

    Returns:
        a pandas DataFrame

    Example:
        # fetch a DataFrame of high-income countries
        df = wbgapi.economy.DataFrame(wbgapi.income.members('HIC'))
    '''

    if pd is None:
        raise ModuleNotFoundError('you must install pandas to use this feature')

    df = None
    row_key = 'value' if labels else 'id'

    for row in list(id,labels=True, skipAggs=skipAggs, db=db):
        if df is None:
            columns = builtins.list(row.keys())
            columns.remove('id')
            columns.remove('value')
            df = pd.DataFrame(columns=['name']+columns)

        key = row['id']
        name = row['value']
        del(row['id'])
        del(row['value'])
        values = map(lambda x: x[row_key] if type(x) is dict else (np.nan if x is None else x), builtins.list(row.values()))
        df.loc[key] = [name] + builtins.list(values)

    return df

def aggregates():
    '''Returns a set object with both the 2-character and 3-character codes
    of aggregate economies. These are obtained from the API and then cached.
    '''

    global _aggs

    update_caches()
    return _aggs

def update_caches():
    '''Update internal metadata caches. This needs to be called prior to
    any fetch from an economy endpoint
    '''
    global _localized_metadata, _iso2Codes, _class_data, _aggs

    if _localized_metadata.get(w.lang):
        # nothing to do
        return

    # update translation data here except city names
    db = {}
    for elem in ['region', 'incomelevel', 'lendingtype']:
        for row in w.fetch(elem):
            if 'name' in row:
                db[row['code']] = row['name'].strip()
            else:
                db[row['id']] = row['value'].strip()

            _iso2Codes[row['id']] = row['iso2code']

    _localized_metadata[w.lang] = db

    url = 'country/all'
    if type(_class_data) is not dict:
        # initialize objects
        _class_data = {}
        _aggs = set()

        # here, we update codes and city translations simultaneously
        for row in w.fetch(url):
            _iso2Codes[row['id']] = row['iso2Code']
            _localized_metadata[w.lang]['capitalCity:'+row['id']] = row['capitalCity'].strip()

            db = {'aggregate': row['region']['id'] == 'NA'}
            for key in ['longitude', 'latitude']:
                db[key] = float(row[key]) if len(row[key]) else None

            for key in ['region', 'adminregion', 'lendingType', 'incomeLevel']:
                db[key] = '' if db['aggregate'] else row[key]['id']

            _class_data[row['id']] = db
            if db['aggregate']:
                _aggs.add(row['id'])
                _aggs.add(row['iso2Code'])

        # add one dummy that we can match to unrecognized economy codes
        db = _class_data['USA']
        _class_data['___'] = {k:None for k in db.keys()}

    else:
        # else, just update city codes
        for row in w.fetch(url):
            _localized_metadata[w.lang]['capitalCity:'+row['id']] = row['capitalCity'].strip()
            

def iso2(code):
    '''Return the iso2 code for a given iso3 code.

    Parameters:

        code:       iso3 code

    Returns:

        And iso2 code, or None

    Notes:
        iso2 codes are not used in the module, but this function is provided as
        a convenience if you need it.
        
    '''

    global _iso2Codes

    update_caches()
    return _iso2Codes.get(code)

def info(id='all',skipAggs=False, db=None):
    '''Print a user report of economies

    Arguments:
        id:         an economy identifier or list-like

        skipAggs:   skip aggregates

    Returns:
        None
    '''

    return w.Featureset(list(id, skipAggs=skipAggs, db=db), ['id', 'value', 'region', 'incomeLevel'])
