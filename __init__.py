
'''This module provides a very rudimentary interface to the World Bank's data API.

Currently only low-level functionality is defined, but the aspiration is this
will improve over time to take advantage of the latest API functionality, as
well as perhaps compensate for some of its flaws.
'''

import urllib
import requests

class APIError(Exception):
  def __init__(self,url,msg,code=None):
    self.msg  = msg
    self.url  = url
    self.code = code

  def __str__(self):
    if self.code:
        return 'APIError: [{}] {} ({})'.format(self.code, self.msg, self.url)

    return 'APIError: {} ({})'.format(self.msg, self.url)


def fetch(url,params={}):
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

        url_ = '{}?{}'.format(url, urllib.urlencode(params_))
        result = _queryAPI(url_)

        if totalRecords is None:
            totalRecords = int(result[0]['total'])

        for elem in result[1]:
            yield elem

        recordsRead += int(result[0]['per_page'])
        params_['page'] += 1

def get(url,params={}):
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

    url_ = url + '?' + urllib.urlencode(params_)
    result = _queryAPI(url_)
    return result[1][0]


def _queryAPI(url):
    '''Internal function for calling the API with sanity checks
    '''
    response = requests.get(url)
    if response.status_code != 200:
        raise wbgapi.APIError(url, response.reason, response.status_code)

    try:
        result = response.json()
    except:
        raise wbgapi.APIError(url, 'JSON decoding error')

    if len(result) < 2:
        if result[0].get('message'):
            msg = result[0]['message'][0]
            raise wbgapi.APIError(url, '{}: {}'.format(msg['key'], msg['value']))
        else:
            raise wbgapi.APIError(url, 'Unrecognized JSON response')

    return result
