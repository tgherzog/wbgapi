
# WBGAPI #

WBGAPI provides modern, pythonic access to the World Bank's data API.
It is designed both for data novices and data scientist types. 

WBGAPI differs from other packages for World Bank data in a few respects and in general tries
to take full advantage of the World Bank's powerful API while mitigating
the impact of some its ideosyncracies. The most significant difference
from other packages is that WBGAPI queries databases individually instead
of collectively. By default, WBGAPI queries the World Development Indicators
database (db=2) but the default can be changed for each request or globally.
This prevents confusion when indicators such as population (SP.POP.TOTL)
appear in several different databases or when different databases have
different dimensions, economies or time periods.

Other key features:

* Easily select multiple series, economies (countries) and time periods in a single request

* Select individual years, ranges, and most recent values (MRVs)

* Metadata queries

* Very "pythonic": use of generators, ranges and sets make data access easy and elegant

* Extensive (but optional) [pandas][pandas] support

## Installation ##

    pip install wbgapi

## Quick Start ##

Import the module; my preferred namespace is `wb`:

    import wbgapi as wb

WBGAPI includes extenstive docstrings with lots of examples:

    help(wb)  
    help(wb.series)  
    [etc]

## Design Overview ##

WBGAPI includes sub-packages for major features in the World Bank API:

Feature   | Description
--------- | -----------
series    | Indicators (e.g., 'SP.POP.TOTL')
economy   | Countries and economies (could be subnational for some databases)
time      | Time (usually annual, sometimes quarterly or monthly)
source    | Databases (e.g., WDI, Doing Business, International Debt)
region    | World Bank regions (this is global to all databases)
income    | World Bank income groups (also global)
lending   | World Bank lending types (also global)
topic     | World Bank topics (this is also a global list and discrete from the Topic metadata field for series)

Each of the above implements a minimum of four functions for accessing and displaying elements of that feature:

Function   | Description
---------- | -----------
`list`     | Returns an iterable list (python generator) of elements
`get`      | Returns a single element, e.g. `get('SP.POP.TOTL')`
`info`     | Like `list` but returns a human-readable table
`Series`   | Like `list` but returns a pandas Series

## Looking Around ##

In interactive mode or a jupyter notebook, the `info` functions are great for exploring what's in the API
or a particular database. A good place to start is by listing the available databases:

    import wbgapi as wb
    
    wb.source.info()
    id    name                                                                  lastupdated
    ----  --------------------------------------------------------------------  -------------
    1     Doing Business                                                        2019-10-23
    2     World Development Indicators                                          2020-12-16
    3     Worldwide Governance Indicators                                       2020-09-28
    5     Subnational Malnutrition Database                                     2016-03-21
    6     International Debt Statistics                                         2021-01-21
    ...
          63 elements

From there, you can inspect the contents of individual databases:

    wb.series.info()        # WDI by default
    wb.economy.info(db=6)   # economies in the Debt Statistics database
    wb.db = 1               # Change default database to...
    wb.series.info()        # ...Doing Business

`info`, `list` and `Series` also let you pass an identifier or list of identifiers to filter the printout:

    wb.series.info('NY.GDP.PCAP.CD')           # GDP
    wb.economy.info(['CAN', 'USA', 'MEX'])     # Countries in North America

You can also query by keyword:

    wb.series.info(q='women')
    wb.economy.info(q='congo')

**Note:** keyword queries ignore the parenthetical part of the indicator name. For example,
`q='GDP'` will not match "Gross domestic savings (% of GDP)". To search the parenthetical part too, add
an exclamation point like this: `q='!GDP'`

Additionally, the `region`, `income`, `lending`, and `topic` sub-packages have a `members` function
that returns the membership of the specfied group, so you can do this:

    wb.economy.info(wb.income.members('HIC'))      # high-income economies
    wb.series.info(wb.topic.members(8))            # indicators in the health topic (wb.topic.info() for full list)
    wb.series.info(topic=8)                        # same as above but easier to type

If that doesn't do it, the `search` function provides deeper search on all metadata in the current database:

    wb.search('fossil fuels')

When you need programmatic access, just call `list` or `Series` instead of `info` in the above examples.

## Accessing Data ##

The `data` sub-package requests data for combinations of series, economies, and time periods in the current
database. Use the `fetch` function to return rows as dictionary objects:

    for row in wb.data.fetch('SP.POP.TOTL', 'USA'): # all years
        print(row)

Or `DataFrame` to return a pandas data frame:

    wb.data.DataFrame(['NY.GDP.PCAP.CD', 'SP.POP.TOTL'], 'CAN', mrv=5) # most recent 5 years 

Each of those parameters (series, economy, time) accepts a single identifier, a list of identifiers, or the default keyword 'all':

    # population for African countries, every other year
    wb.data.DataFrame('SP.POP.TOTL', wb.region.members('AFR'), range(2010, 2020, 2))

Both `fetch` and `DataFrame` provide a lot of paramters for customizing your request, so use the help function to check
the documentation.

Note that `DataFrame` will use multi-indexes where necessary (use the "index" and "columns" parameters to change the
default behavior)::

    wb.data.DataFrame(['SP.POP.TOTL', 'EN.ATM.CO2E.KT'], time=range(2000, 2020), skipBlanks=True, columns='series')

                    EN.ATM.CO2E.KT  SP.POP.TOTL
    economy time                               
    ABW     YR2000        2379.883      90853.0
            YR2001        2409.219      92898.0
            YR2002        2438.555      94992.0
            YR2003        2563.233      97017.0
            YR2004        2618.238      98737.0
    ...                        ...          ...
    ZWE     YR2015       12317.453   13814629.0
            YR2016       10982.665   14030390.0
            YR2017             NaN   14236745.0
            YR2018             NaN   14439018.0
            YR2019             NaN   14645468.0
 
Use the `reset_index` function (on the data frame) to replace the index with 0-based integers:

    wb.data.DataFrame('SP.POP.TOTL', time=2015, labels=True).reset_index()

        economy                         Country   SP.POP.TOTL
    0       ZWE                        Zimbabwe  1.381463e+07
    1       ZMB                          Zambia  1.587936e+07
    2       YEM                     Yemen, Rep.  2.649789e+07
    3       PSE              West Bank and Gaza  4.270092e+06
    4       VIR           Virgin Islands (U.S.)  1.077100e+05
    ..      ...                             ...           ...

Most World Bank databases consist of 3 dimensions: series, economy and time. But some, like WDI Archives,
contain 4 dimensions, which you can access like this:

    wb.source.concepts(db=57)

    {'economy': {'key': 'country', 'value': 'Country'},
     'series': {'key': 'series', 'value': 'Series'},
     'time': {'key': 'time', 'value': 'Time'},
     'version': {'key': 'version', 'value': 'Version'}}

And query like this:

    # Have population estimates for Brazil been revised over time?
    # Version identifiers are in the form YYYYMM. This example queries data for the April
    # versions from 2010-2019
    wb.data.DataFrame('SP.POP.TOTL', 'BRA', range(2000,2005), version=range(201004,202004,100), db=57)
                  YR2000       YR2001       YR2002       YR2003       YR2004
    version                                                                 
    201004   174174447.0  176659138.0  179123364.0  181537359.0  183863524.0
    201104   174174447.0  176659138.0  179123364.0  181537359.0  183863524.0
    201204   174425387.0  176877135.0  179289227.0  181633074.0  183873377.0
    201304   174425387.0  176877135.0  179289227.0  181633074.0  183873377.0
    201404   174504898.0  176968205.0  179393768.0  181752951.0  184010283.0
    201504   174504898.0  176968205.0  179393768.0  181752951.0  184010283.0
    201604   175786441.0  178419396.0  181045592.0  183627339.0  186116363.0
    201704   175786441.0  178419396.0  181045592.0  183627339.0  186116363.0
    201804   175287587.0  177750670.0  180151021.0  182482149.0  184738458.0
    201904   175287587.0  177750670.0  180151021.0  182482149.0  184738458.0
    

## Non-Standard and Custom Dimensions ##

WBGAPI tries to provide some level of normalization for dimensions in API databases. As suggested
above, the 'economy' dimension is referenced as 'economy' even though the target database
may defined it as 'state,' 'province' or something else. Similarly, 'year' becomes 'time.'
Reserved characters are mapped to underscores so you can pass them as function arguments.
Again, the `concepts` function shows what is going on behind the scenes:

    wb.source.concepts(db=6)

    {'counterpart_area': {'key': 'counterpart-area', 'value': 'Counterpart-Area'},
     'economy': {'key': 'country', 'value': 'Country'},
     'series': {'key': 'series', 'value': 'Series'},
     'time': {'key': 'time', 'value': 'Time'}}

The standard dimensions all support the Series function to provide elements as a
pandas Series (see above), but they all share a common implemention function which you can
call yourself. Here's how to get a Series for a custom dimension:

    wb.Series(wb.source.features('counterpart_area', db=6))


## Access the Economies Data Frame ##

As explained above, any feature in WBGAPI can be returned as a pandas Series. In addition economies
can also be returned as a DataTable with region, income, and lending codes:

    wb.economy.DataFrame()

Or to limit exclude the aggregate regions:

    wb.economy.DataFrame(skipAggs=False)


## Accessing Metadata ##

wbgapi returns metadata for series, economies and combinations:

    wb.series.metadata.get('SP.POP.TOTL', economies=['KEN', 'TZA'])

or single footnotes:

    wb.data.footnote('SP.POP.TOTL', 'ARG', 2010)

## Resolving Country Names ##

wbgapi includes utility function that resolves common spellings of country names to the ISO3 codes used by the API. The
return from this function is a "dict" subclass that provides a nice report, but can still be processed programmatically:

    wb.economy.coder(['Argentina', 'Swaziland', 'South Korea', 'England', 'Chicago'])
    ORIGINAL NAME    WBG NAME        ISO_CODE
    ---------------  --------------  ----------
    Argentina        Argentina       ARG
    Swaziland        Eswatini        SWZ
    South Korea      Korea, Rep.     KOR
    England          United Kingdom  GBR
    Chicago

## Customizing the Display ##

wbgapi provides fairly good support for IPython, Jupyter Notebook, etc and will generally return HTML
output for things like tables in those environments. HTML output is wrapped in a `<div class="wbgapi"/>`
container so that you can customize the CSS if you so desire (for instance, I like to left-align the columns).
The location of your custom.css varies depending on your environment. Note that this does not apply
to DataFrame objects, which are formatted by pandas.

## Proxy Servers and Other HTTP Options ##

WBGAPI uses [requests][requests] for all HTTP/HTTPS calls. As of version 1.0.10
you can use the `get_options` module variable to pass any additional parameters you like to
`requests.get` for instance, to specify a
[proxy server](https://requests.readthedocs.io/en/master/user/advanced/#proxies) or
[disable SSL verification](https://requests.readthedocs.io/en/master/user/advanced/#ssl-cert-verification).
For example:

    wb.get_options['proxies'] = {
       'http': 'http://10.10.1.10:3128',
       'https': 'http://10.10.1.10:1080',
    }

Using the `wb.proxies` variable is still supported on a deprecated basis and will raise a DeprecationWarning
exception (which python ignores by default).

## Caching ##

WBGAPI has no built-in caching, but you can implement it yourself using
[requests cache][req-cache].


[beta-endpoints]: https://datahelpdesk.worldbank.org/knowledgebase/articles/1886686-advanced-data-api-queries
[pandas]: https://pandas.pydata.org
[sunset]: https://www.python.org/doc/sunset-python-2/
[requests]: https://requests.readthedocs.io/en/master/
[req-cache]: https://pypi.org/project/requests-cache/

