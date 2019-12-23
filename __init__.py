
'''This module provides a very rudimentary interface to the World Bank's data API.
'''

import urllib.parse
import requests
from . import series
from . import source
from . import economy
from . import time
from . import data

# defaults
endpoint = 'https://api.worldbank.org/v2'
lang = 'en'
db = 2
economy_key = 'economy' # used to map a database's economy dimension to a standard constant

class APIError(Exception):
  def __init__(self,url,msg,code=None):
    self.msg  = msg
    self.url  = url
    self.code = code

  def __str__(self):
    if self.code:
        return 'APIError: [{}] {} ({})'.format(self.code, self.msg, self.url)

    return 'APIError: {} ({})'.format(self.msg, self.url)


def fetch(url,params={},concepts=False):
    '''Iterate over an API response with automatic paging

    Parameters:
        url: full URL for the API query, minus the query string

        params: optional query string parameters (required defaults are supplied by the function)

    Returns:
        a generator object

    Example:
        for row in wbgapi.fetch('https://api.worldbank.org/countries'):
          print row['name']
    '''

    params_ = {'per_page': 100}
    params_.update(params)
    params_['page'] = 1
    params_['format'] = 'json'

    totalRecords = None

    recordsRead = 0
    while totalRecords is None or recordsRead < totalRecords:

        url_ = '{}?{}'.format(url, urllib.parse.urlencode(params_))
        (hdr,result) = _queryAPI(url_)

        if totalRecords is None:
            totalRecords = int(hdr['total'])

        data = _responseObjects(url_, result, wantConcepts=concepts)
        for elem in data:
            yield elem

        recordsRead += int(hdr['per_page'])
        params_['page'] += 1

def get(url,params={},concepts=False):
    '''Return a single response from the API

    Parameters:
        url: full URL for the API query, minus the query string

        params: optional query string parameters (required defaults are supplied by the function)

    Returns:
        First row from the response

    Example:
        print wbgapi.get('https://api.worldbank.org/countries/BRA')['name']
    '''

    params_ = params.copy()
    params_['page'] = 1
    params_['format'] = 'json'
    params_['per_page'] = 1

    url_ = url + '?' + urllib.parse.urlencode(params_)
    (hdr,result) = _queryAPI(url_)
    data = _responseObjects(url_, result, wantConcepts=concepts)
    return data[0] if len(data) > 0 else None


def _responseHeader(url, result):
    '''Internal function to return the response header, which contains page information
    '''

    if type(result) is list and len(result) > 0 and type(result[0]) is dict:
        # looks like the v2 data API
        return result[0]

    if type(result) is dict:
        # looks like the new beta advanced API
        return result

    raise APIError(url, 'Unrecognized response object format')

def _responseObjects(url, result, wantConcepts=False):
    '''Internal function that returns an array of objects
    '''

    if type(result) is list and len(result) > 1:
        # looks like the v2 data API
        return result[1]

    if type(result) is dict and result.get('source'):
        if type(result['source']) is list and len(result['source']) > 0 and type(result['source'][0]) is dict:
            # this format is used for metadata and concept lists. Caller may need an array of concepts or
            # an array of the variables of the first concept
            if wantConcepts:
                return result['source'][0]['concept']
            else:
                return result['source'][0]['concept'][0]['variable']

        if type(result['source']) is dict:
            # this format is used to return data in the beta endpoints
            return result['source']['data']

    raise APIError(url, 'Unrecognized response object format')

def _queryAPI(url):
    '''Internal function for calling the API with sanity checks
    '''
    response = requests.get(url)
    if response.status_code != 200:
        raise APIError(url, response.reason, response.status_code)

    try:
        result = response.json()
    except:
        raise APIError(url, 'JSON decoding error')

    hdr = _responseHeader(url, result)
    if hdr.get('message'):
        msg = hdr['message'][0]
        raise APIError(url, '{}: {}'.format(msg['key'], msg['value']))

    return (hdr, result)

def queryParam(arg):
    ''' convert an API parameter to a semicolon-delimited string
    '''

    if type(arg) is str or type(arg) is int:
        return str(arg)

    if type(arg) is list:
        return ';'.join(map(lambda x:str(x), arg))

    return None

