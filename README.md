
# WBGAPI #

WBGAPI provides modern, pythonic access to the World Bank's data API.
It is designed both for data novices and data scientist types. 
WBGAPI tries to shield users from some of the confusing ideosyncrasies
of the World Bank's API while remaining consistent and intuitive for
those who are familiar with its basic data structures.

WBGAPI differs from other modules in a few respects. The most significant
is that it queries databases individually instead of collectively. To appreciate
the difference, consider this API request:

https://api.worldbank.org/v2/indicator

As of this writing, this request returns 17,473 resulting indicators. But what
this obscures is that these indicators are stored in 61 separate databases,
updated on different schedules, and covering different time spans and country
groups. Many indicators appear in more than one database. While it's possible
to use the API to get more precise results, it's not always easy to understand
what you're requesting or where it's actually coming from.

WBGAPI fixes this issue by only querying a single database at a time using a [relatively
new set of endpoints][beta-endpoints]. This gives users an accurate picture
of both the data, dimensions and features of that database. The default database
is the World Development Indicators (WDI) but you can target different databases
either globally or with each request.

Other key features:

* Easily select multiple series, economies (countries) and time periods in a single request

* Select individual years, ranges, and most recent values (MRVs)

* Metadata queries

* Very "pythonic": use of generators, ranges and sets make data access easy and elegant

* Extensive [pandas][pandas] support (optional)

## Installation ##

    pip install wbgapi

## Quick Start ##

Import the module; my preferred namespace is `wb`:

    import wbgapi as wb

WBGAPI includes extenstive docstrings with lots of examples:

    help(wb)  
    help(wb.series)  
    [etc]

Every element type is its own object: source, series, region, time,
etc. Note that "countries" and aggregates are accessed through the "economy"
object and the time dimension is always accessed through the time object.
All World Bank databases have a series, time, and economy dimension,
although the API is not consistent in its concept scheme across databases.
For example, in some databases the economy dimension is called 'economy' or 'province'
instead of 'country' and the time dimension is sometimes called 'year.'
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

    stuff = {i['id']: i['value'] for i in wb.series.list(['SP.POP.TOTL', 'SI.POV.NAHC'])}
    stuff
    {'SP.POP.TOTL': 'Population, total', 'SI.POV.NAHC': 'Poverty headcount ratio at national poverty lines (% of population)'}

Any single identifier or iterable object can generally be passed as an argument to select series, economies, regions, and so forth.
Here's an easy way to get a list of high-income countries:

    for row in wb.economy.list(wb.region.members('HIC')):
        print(row['value'])

### Data Requests ###

Again, use `fetch()` for multiple rows of data, and `get()` for single rows. Python ranges are an easy way to
indicate which time periods you want.

    # this request fetches data for 3 countries from 2010-2015. Be careful with requests
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

    for row in wb.data.fetch('SP.POP.TOTL', mrnev=1, skipAggs=True, labels=True):
        print(row['economy'], row['value'])

    {'id': 'AFG', 'value': 'Afghanistan', 'aggregate': False} 37172386
    {'id': 'ALB', 'value': 'Albania', 'aggregate': False} 2866376
    {'id': 'DZA', 'value': 'Algeria', 'aggregate': False} 42228429
    {'id': 'ASM', 'value': 'American Samoa', 'aggregate': False} 55465
    ...

### Pandas ###

Data and economy queries can be returned as pandas DataFrames. For example:

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

And then aggregate (albeit unweighted):

    df.groupby('incomeLevel').mean()
                       YR2010        YR2012        YR2014        YR2016        YR2018
    incomeLevel                                                                      
    HIC          1.436314e+07  1.451850e+07  1.469533e+07  1.487142e+07  1.502200e+07
    LIC          1.862174e+07  2.012211e+07  2.113464e+07  2.222469e+07  2.339882e+07
    LMC          5.720078e+07  5.898364e+07  6.076860e+07  6.254959e+07  6.431713e+07
    UMC          4.165684e+07  4.229376e+07  4.296426e+07  4.363008e+07  4.426060e+07

Of course, these DataFrames can be used for any sort of analysis and operations that pandas supports,
and can be used with lots of various visualization libraries. Time series can be easily plotted by transposing a DataFrame:

    wb.data.DataFrame('NY.GDP.PCAP.CD', ['BRA', 'ARG'], time=range(2000,2020),numericTimeKeys=True).transpose().plot()

Use pandas' `reset_index` option to fetch unindexed columns of indicators:

    wb.data.DataFrame(['SP.POP.TOTL', 'NY.GDP.PCAP.CD', 'EN.ATM.CO2E.KT'],time=range(2000,2010), numericTimeKeys=True, columns='series').reset_index()
          time economy  EN.ATM.CO2E.KT  NY.GDP.PCAP.CD  SP.POP.TOTL
    0     2000     ABW        2379.883    20620.700626      90853.0
    1     2000     AFG         773.737             NaN   20779953.0
    2     2000     AGO        9541.534      556.836318   16395473.0
    3     2000     ALB        3021.608     1126.683318    3089027.0
    4     2000     AND         524.381    21936.530101      65390.0
    ...    ...     ...             ...             ...          ...
    2635  2009     XKX             NaN     3209.711460    1761474.0
    2636  2009     YEM       24561.566     1116.084594   22516460.0
    2637  2009     ZAF      503112.400     5862.797340   50477011.0
    2638  2009     ZMB        2508.228     1159.907762   13215139.0
    2639  2009     ZWE        5603.176      771.598786   12526968.0


### Switching databases ###

Use the `source` object to learn about other databases and the `db` variable to change the global database target:

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

Most functions also accept a `db` parameter to specify the database as an argument. This option will override the global option.


### Custom Dimensions ###

Most databases consist of 3 dimensional concepts: `series`, `country` and `time`. But this is not always the case: several databases use `economy`, `state`
or something else in lieu of `country` and at least one uses `year` in lieu of `time`. To make programming more intuitive, wbgapi normalizes common
dimensions as `economy` and `time` so that you don't have to guess (this includes subnational databases, since at this point all databases capture
all administrative levels in the same dimension).

You can access a database's actual concept structure like this:

    for k,v in wb.source.concepts().items():
        print(k, v)

Some databases have additional dimensions; for instance, WDI Archives (57) has a version dimension. Simply pass these as additional parameters,
or omit them to return all features in the dimension. Python ranges work where where dimensions are numeric. For example, to retrieve population
data for all WDI versions in 2019, do this:

    for row in wb.data.fetch('SP.POP.TOTL', ['BRA', 'COL', 'ARG'], time=range(2010,2015), version=range(201901,201912), wb.db=57):
      ...

or:

    for row in wb.data.fetch('SP.POP.TOTL', ['BRA', 'COL', 'ARG'], time=range(2010,2015), version=range(201901,201912), db=57):
      ...

wbgapi will create multi-index DataFrames where necessary, although you may need to fiddle with the index and column parameters to get what you want.
Here is how to run the same query arranged to more easily compare different versions of the same series:

    wb.data.DataFrame('SP.POP.TOTL', ['BRA', 'COL', 'ARG'], time=range(2010,2015), version=range(201901,201912), index=['economy', 'version'], db=57)

                     YR2010       YR2011       YR2012       YR2013       YR2014
    ARG 201901   41223889.0   41656879.0   42096739.0   42539925.0   42981515.0
        201903   41223889.0   41656879.0   42096739.0   42539925.0   42981515.0
        201904   41223889.0   41656879.0   42096739.0   42539925.0   42981515.0
        201906   40788453.0   41261490.0   41733271.0   42202935.0   42669500.0
    ...
    BRA 201901  196796269.0  198686688.0  200560983.0  202408632.0  204213133.0
        201903  196796269.0  198686688.0  200560983.0  202408632.0  204213133.0
        201904  196796269.0  198686688.0  200560983.0  202408632.0  204213133.0
        201906  195713635.0  197514534.0  199287296.0  201035903.0  202763735.0
    ...
    COL 201901   45918097.0   46406646.0   46881475.0   47342981.0   47791911.0
        201903   45918097.0   46406646.0   46881475.0   47342981.0   47791911.0
        201904   45918097.0   46406646.0   46881475.0   47342981.0   47791911.0
        201906   45222700.0   45663099.0   46076848.0   46497267.0   46969209.0
    ...

### Metadata ###

wbgapi returns metadata for series, economies and combinations:

    wb.series.metadata.get('SP.POP.TOTL', economies=['KEN', 'TZA'])

    for i in wb.economy.metadata.get('all'):
      print(i)

or single footnotes:

    print(wb.data.footnote('SP.POP.TOTL', 'FRA', 2015))

### Resolving Country Names ###

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

---

Hopefully that gives you a taste and enough to get started. Use `help()` and read the docstrings for lots more examples, information, and ideas.

## Customizing the Display ##

wbgapi provides fairly good support for IPython, Jupyter Notebook, etc and will generally return HTML
output for things like tables in those environments. HTML output is wrapped in a `<div class="wbgapi"/>`
container so that you can customize the CSS if you so desire (for instance, I like to left-align the columns).
The location of your custom.css varies depending on your environment. Note that this does not apply
to DataFrame objects, which are formatted by pandas.

## Proxy servers ##

`wbgapi.proxies` can be configured to support proxy servers. This variable is passed
[directly to the requests module](https://requests.readthedocs.io/en/master/user/advanced/#proxies).

    wb.proxies = {
      'http': 'http://10.10.1.10:3128',
      'https': 'http://10.10.1.10:1080',
    }

## Limitations ##

* WBGAPI requires Python 3.x (it's 2020, and the [sun has set on Python 2.x][sunset]). Time
  to move on if you haven't already.

* WBGAPI is fully multi-lingual. However, as of this writing, the API endpoints it depends
  on are returning English-only, which means that in practice the module is English-only as well.
  Short of some serious hacks which have their own negative consequences, it's not really possible
  to fix this until the API itself sees some improvements.

* WBGAPI has no built-in caching. However, it makes all its requests through [requests][requests], which
  can be cached via [requests cache][req-cache]

[beta-endpoints]: https://datahelpdesk.worldbank.org/knowledgebase/articles/1886686-advanced-data-api-queries
[pandas]: https://pandas.pydata.org
[sunset]: https://www.python.org/doc/sunset-python-2/
[requests]: https://requests.readthedocs.io/en/master/
[req-cache]: https://pypi.org/project/requests-cache/

