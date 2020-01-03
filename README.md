
# WBGAPI #

WBGAPI provides modern, pythonic access to the World Bank's data API.
It is designed both for data novices and data scientist types. 
WBGAPI tries to shield users from some of the confusing ideosyncrasies
of the World Bank's API while remaining consistent and intuitive for
those who are familiar with its basic data structures. More on that later.

WBGAPI differs from other modules in a few respects. The most significant
is that it queries databases individually instead of collectively. To appreciate
the difference, consider this API request:

https://api.worldbank.org/v2/indicator

As of this writing, this request returns 17,328 resulting indicators. But what
this obscures is that these indicators are stored in 57 separate databases,
updated on different schedules, and covering different time spans and country
groups. Many indicators appear in more than one database. While it's possible
to use the API to get more precise results, it's not always easy to understand
what you're requesting or where it's actually coming from.

WBGAPI fixes this issue by only querying a single database at a time using a [relatively
new set of endpoints][beta-endpoints]. This gives users an accurate picture
of both the data, dimensions and features of that database. The default database
is the World Development Indicators (WDI) but you can switch databases at any time.

Other key features:

* Easily select multiple series, economies (countries) and time periods in a single request

* Select individual years, ranges, and most recent values (MRVs)

* Metadata queries

* Very "pythonic": use of generators, ranges and sets make data access easy and elegant

* Extensive [pandas][pandas] support (optional)

* Multi-lingual support (sort of. See "Limitations" section below)

## Installation ##

WBGAPI is currently in alpha development and is not yet on PyPl. But you can still use
pip to install directly from github:

    pip install git+https://github.com/tgherzog/wbgapi.git

## Quick Start ##

Import the module; my preferred namespace is `wb`:

    import wbgapi as wb

WBGAPI includes extenstive docstrings with lots of examples:

    help(wb)  
    help(wb.series)  
    [etc]

Every element type is its own object: source, series, region, time,
etc. Note that "countries" and aggregates are accessed through the "economy"
object. All World Bank databases have a series, time, and economy dimension,
although the API is not consistent in its concept scheme across databases.
The WBGAPI module saves you most of that headache.

Objects tend to use a common set of functions which you'll use heavily:

* `list()` returns an interative list of basic data elements. Actually, it returns a python generator.
  You can pass parameters to limit the list, but by default it returns all elements
  in the database.

* `get()` returns a single object.

* `info()` prints a summary report of objects: all elements by default. These are great
  if you just want to quickly see what's in a database.

* `fetch()` functions return data and metadata. They usually involve more arguments
  and return more complicated objects, but are otherwise similar to `list()`

Alrighty then, let's fire it up:

    import wbgapi as wb

    # show the series list
    wb.series.info()
    id                         value
    AG.AGR.TRAC.NO             Agricultural machinery, tractors
    AG.CON.FERT.PT.ZS          Fertilizer consumption (% of fertilizer production)
    AG.CON.FERT.ZS             Fertilizer consumption (kilograms per hectare of arable land)
    AG.LND.AGRI.K2             Agricultural land (sq. km)
    AG.LND.AGRI.ZS             Agricultural land (% of land area)
    AG.LND.ARBL.HA             Arable land (hectares)
    AG.LND.ARBL.HA.PC          Arable land (hectares per person)
    AG.LND.ARBL.ZS             Arable land (% of land area)
    ...
                               1429 elements

    wb.time.info()
    id      value
    YR1960  1960
    YR1961  1961
    YR1962  1962
    YR1963  1963
    YR1964  1964
    ...
            60 elements

That first command will take a while and run a very long report due to the size of the WDI.

Use `get()` and `list()` to access the underlying objects:

    wb.economy.get('COL')
    {'id': 'COL', 'value': 'Colombia', 'aggregate': False, 'longitude': -74.082, 'latitude': 4.60987, 'region': 'LCN', 'adminregion': 'LAC', 'lendingType': 'IBD', 'incomeLevel': 'UMC', 'capitalCity': 'Bogota'}

    for row in wb.series.list(['SP.POP.TOTL', 'SI.POV.NAHC']):
        stuff[row['id']] = row['value']

    stuff
    {'SP.POP.TOTL': 'Population, total', 'SI.POV.NAHC': 'Poverty headcount ratio at national poverty lines (% of population)'}

API veterans might notice that the objects use `value` for element names instead of `name`. That's an artifact of the "advanced" queries
mentioned previously.

Any single identifier or iterable object can be used to select series, economies, regions, and so forth. Here's an easy way to get
a list of high-income countries:

    for row in wb.economy.list(wb.region.members('HIC')):
        print(row['value'])

### Data Requests ###

Again, use `fetch()` for multiple rows of data, and `get()` for single rows:

    # this request fetches data for 3 countries from 2015 onward. Be careful with requests
    # that omit constraints on economies and/or time as these can take a long time to run
    # and return large numbers of rows
    for row in wb.data.fetch('SP.POP.TOTL', economy=['BRA', 'ARG', 'URY'], time=range(2010,2015)):
        print(row)

    {'value': 3400434, 'series': 'SP.POP.TOTL', 'economy': 'URY', 'aggregate': False, 'time': 'YR2014'}
    {'value': 3389439, 'series': 'SP.POP.TOTL', 'economy': 'URY', 'aggregate': False, 'time': 'YR2013'}
    {'value': 3378974, 'series': 'SP.POP.TOTL', 'economy': 'URY', 'aggregate': False, 'time': 'YR2012'}
    ...
    {'value': 13082.664325572, 'series': 'NY.GDP.PCAP.CD', 'economy': 'ARG', 'aggregate': False, 'time': 'YR2012'}
    {'value': 12848.8641969705, 'series': 'NY.GDP.PCAP.CD', 'economy': 'ARG', 'aggregate': False, 'time': 'YR2011'}
    {'value': 10385.9644319555, 'series': 'NY.GDP.PCAP.CD', 'economy': 'ARG', 'aggregate': False, 'time': 'YR2010'}

Or if you want the most recent value for every country (omitting aggregates), including both element codes and labels:

    for row in wb.data.fetch('SP.POP.TOTL', mrnev=1,skipAggs=True,labels=True):
        print(row['economy'], row['value')

    {'id': 'AFG', 'value': 'Afghanistan', 'aggregate': False} 37172386
    {'id': 'ALB', 'value': 'Albania', 'aggregate': False} 2866376
    {'id': 'DZA', 'value': 'Algeria', 'aggregate': False} 42228429
    {'id': 'ASM', 'value': 'American Samoa', 'aggregate': False} 55465
    ...

### Pandas ###

You can also return most queries as pandas DataFrames or Series. For example:

    # data frame of population data for even-numbered years
    wb.data.DataFrame('SP.POP.TOTL', time=range(2010,2020,2),labels=True)
                Label      YR2010      YR2012      YR2014      YR2016      YR2018
    ABW         Aruba    101669.0    102560.0    103774.0    104872.0    105845.0
    AFG   Afghanistan  29185507.0  31161376.0  33370794.0  35383128.0  37172386.0
    AGO        Angola  23356246.0  25107931.0  26941779.0  28842484.0  30809762.0
    ALB       Albania   2913021.0   2900401.0   2889104.0   2876101.0   2866376.0
    AND       Andorra     84449.0     82427.0     79213.0     77297.0     77006.0
    ..            ...         ...         ...         ...         ...         ...
    XKX        Kosovo   1775680.0   1805200.0   1821800.0   1816200.0   1845300.0
    YEM   Yemen, Rep.  23154855.0  24473178.0  25823485.0  27168210.0  28498687.0
    ZAF  South Africa  51216964.0  52834005.0  54545991.0  56203654.0  57779622.0
    ZMB        Zambia  13605984.0  14465121.0  15399753.0  16363507.0  17351822.0
    ZWE      Zimbabwe  12697723.0  13115131.0  13586681.0  14030390.0  14439018.0

`economy`, `region`, `income`, and `lending` can also return Pandas objects. Here is how you might add the income group to the query above:

    c = wb.economy.DataFrame()
    df = wb.data.DataFrame('SP.POP.TOTL', time=range(2010,2020,2),labels=True,skipAggs=True).join(c['incomeLevel'])
    df
                Label      YR2010      YR2012      YR2014      YR2016      YR2018 incomeLevel
    ABW         Aruba    101669.0    102560.0    103774.0    104872.0    105845.0         HIC
    AFG   Afghanistan  29185507.0  31161376.0  33370794.0  35383128.0  37172386.0         LIC
    AGO        Angola  23356246.0  25107931.0  26941779.0  28842484.0  30809762.0         LMC
    ALB       Albania   2913021.0   2900401.0   2889104.0   2876101.0   2866376.0         UMC
    AND       Andorra     84449.0     82427.0     79213.0     77297.0     77006.0         HIC
    ..            ...         ...         ...         ...         ...         ...         ...

And then aggregate:

    df.groupby('incomeLevel').mean()
                       YR2010        YR2012        YR2014        YR2016        YR2018
    incomeLevel                                                                      
    HIC          1.436314e+07  1.451850e+07  1.469533e+07  1.487142e+07  1.502200e+07
    LIC          1.862174e+07  2.012211e+07  2.113464e+07  2.222469e+07  2.339882e+07
    LMC          5.720078e+07  5.898364e+07  6.076860e+07  6.254959e+07  6.431713e+07
    UMC          4.165684e+07  4.229376e+07  4.296426e+07  4.363008e+07  4.426060e+07

Of course, these DataFrames can be used for any sort of analysis and operations that pandas supports,
and can be used with lots of various visualization libraries.

### Switching databases ###

Use the `source` object to learn about other databases and the `db` variable to change the query targte:

    wb.source.info()
    id  name
    1   Doing Business
    2   World Development Indicators
    3   Worldwide Governance Indicators
    5   Subnational Malnutrition Database
    ...

    wb.db = 1   # change to Doing Business
    wb.series.info()
    id                                                 value
    ENF.CONT.COEN.ATDR                                 Enforcing contracts: Alternative dispute resolution (0-3) (DB16-20 methodology)
    ENF.CONT.COEN.ATFE.PR                              Enforcing contracts: Attorney fees (% of claim)
    ENF.CONT.COEN.COST.ZS                              Enforcing contracts: Cost (% of claim)
    ...

Hopefully that gives you a taste and enough to get started. Use `help()` and read the docstrings for lots more examples, information, and ideas

## Limitations ##

* WBGAPI requires Python 3.x (it's 2020, and the [sun has set on Python 2.x][sunset]). Time
  to move on.

* WBGAPI is fully multi-lingual. However, as of this writing, the API endpoints it depends
  on are returning English-only. The module returns what the API gives it, regardless of whether
  the response language matches the request. Hopefully the World Bank can improve its implementation
  soon.

* WBGAPI has no built-in caching. However, it makes all its requests through [requests][requests], which
  can be cached via [requests cache][req-cache]

[beta-endpoints]: https://datahelpdesk.worldbank.org/knowledgebase/articles/1886686-advanced-data-api-queries
[pandas]: https://pandas.pydata.org
[sunset]: https://www.python.org/doc/sunset-python-2/
[requests]: https://requests.readthedocs.io/en/master/
[req-cache]: https://pypi.org/project/requests-cache/

