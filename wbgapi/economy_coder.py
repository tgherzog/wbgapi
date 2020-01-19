
'''Translates country names into country codes, based on common
spellings and conventions.
'''

import wbgapi as w
import yaml
import os
import re
from functools import reduce

_lookup_data = None

def lookup(name,debug=None):
    '''Return the country code for a given country name, based on common spellings and conventions.
    This function is intended to make it easier to convert country names to ISO3 codes.

    This feature is English-only and still in development. You can extend the matching algorithm
    by editing the `lookup-data.yaml` file.

    Arguments:

        name:       a country name as a string, or an iterable object of name strings

        debug:      a list of ISO codes for which to print debug output

    Returns:
        If `name` is a string then the function returns the corresponding ISO3 code, or None if the code
        can't be ascertained.

        If `name` is an iterable object, the function returns a dict of country names (passed as arguments)
        and corresponding ISO3 codes. Country names that cannot be ascertained have a value of None

    Examples:
        print(wbgapi.economy.lookup('Eswatini')) # prints 'SWZ'

        print(wbgapi.economy.lookup('Swaziland')) # prints 'SWZ'

        print(wbgapi.economy.lookup(['Canada', 'Toronto']))   # prints {'Canada': 'CAN', 'Toronto': None}
    '''
    global _lookup_data

    def prepare(s, clean=False, magicRegex=False):

        s = s.lower()
        if clean:
            # should be False if the string is regex-capable

            # this next trick is strips the container parentheses from "... (US|UK)"
            # and leaves the inner part. Need this for the Virgin Islands since,
            # before we remove parenthetical text entirely
            s = re.sub(r'\((u\.?s\.?|u\.?k\.?)\)', lambda t: t.group(1).replace('.',''), s)

            s = re.sub(r'\s*\(.*\)', '', s)         # remove parenthetical text
            s = s.replace("'", '')                  # remove apostrophes
            s = re.sub(r'[^a-z0-9&]', ' ', s)       # convert remaining superflous chars to spaces

        s = s.strip()

        if magicRegex:
            # converts 'and' to (and|&), 'st' to (st|saint)
            s = re.sub(r'\band\b', r'(and|\&)', s)
            s = re.sub(r'\bst\b', r'(st|saint)', s)
            s = re.sub(r'\s+', r'\\s+', s)

        return s

    if _lookup_data is None:
        _lookup_data = []
        user_data = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'lookup-data.yaml'), 'r'))

        for row in w.fetch('country/all', lang='en'):
            if row['region']['id'] == 'NA':
                continue # ignore aggregates

            obj = user_data.get(row['id'], {})
            # convert ordinary arrays to objects - for most cases this simplifies the yaml
            if type(obj) is list:
                obj = {'patterns': obj}

            try:
                order = obj.get('order', 10)
            except:
                print(obj)
                raise

            _lookup_data.append((row['id'].lower(), row['id'], False, order))
            _lookup_data.append(('\\b{}\\b'.format(prepare(row['name'], clean=True, magicRegex=True)), row['id'], True, order))
            for row2 in obj.get('patterns',[]):
                if row2[0:1] == ':':
                    # treat as an exact case-insensitive string match
                    _lookup_data.append((row2[1:].lower(), row['id'], False, order))
                else:
                    # treat as a regex string which can match on any word boundary
                    _lookup_data.append(('\\b{}\\b'.format(prepare(row2, clean=False, magicRegex=True)), row['id'], True, order))

        _lookup_data.sort(key=lambda x: x[3])

    if type(name) is str:
        name = [name]
        is_list = False
    else:
        is_list = True

    results = {k: None for k in name}
    for t in name:
        t2 = prepare(t, clean=True, magicRegex=False)
        for pattern,id,mode,order in _lookup_data:
            if debug and id in debug:
                print('{}: matching "{}"/{} against "{}"'.format(id, pattern, mode, t2))

            if mode and re.search(pattern, t2):
                results[t] = id
                break
            elif not mode and pattern == t2:
                results[t] = id
                break

    if is_list:
        return results

    return results.get(name[0])
            
def report(economies):

    c = {row['id']: row['name'] for row in w.fetch('country/all', lang='en') if row['region']['id'] != 'NA'}

    rows = [('ORIGINAL NAME', 'WBG NAME', 'ISO_CODE')]
    for k,v in economies.items():
        if v:
            wb_name = c.get(v, '')
            if wb_name.lower() == k.lower():
                continue
        else:
            wb_name = ''

        rows.append((k, wb_name, v))

    maxName1 = len( reduce(lambda a,b: a if len(a) > len(b) else b, [row[0] for row in rows]) )
    maxName2 = len( reduce(lambda a,b: a if len(a) > len(b) else b, [row[1] for row in rows]) )

    for row in rows:
        print('{col1:{len1}}  {col2:{len2}}  {col3}'.format(col1=row[0], len1=maxName1, col2=row[1], len2=maxName2, col3=row[2]))
