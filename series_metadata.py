
import wbgapi as w

def fetch(id,countries=[],time=[],db=None):
    '''Return metadata for specified series

    Arguments:
        id:         The series ID or an array of series ID's to return metadata for

        countries:  Optional list of countries for which to include series-country metadata

    Returns:
        A generator object
    '''

    pg_size = 50    # large 2-dimensional metadata requests must be paged or the API will barf
                    # this sets the page size. Seems to work well even for very log CETS identifiers

    if type(countries) is str:
        countries = [countries]

    if type(time) is str:
        time = [time]

    if db is None:
        db = w.db

    if not w.source.has_metadata(db):
        return None

    url = '{}/{}/sources/{}/series/{}/metadata'.format(w.endpoint, w.lang, db, w.queryParam(id))
    for row in w.metadata(url):
        if countries:
            row.countries = {}
            n = 0
            while n < len(countries):
                cs = ';'.join(['{}~{}'.format(elem,row.id) for elem in countries[n:n+pg_size]])
                n += pg_size
                url2 = '{}/{}/sources/{}/Country-Series/{}/metadata'.format(w.endpoint, w.lang, db, cs)

                # requests for non-existing data throw malformed responses so we must catch for them
                try:
                    for row2 in w.metadata(url2):
                        # w.metadata should be returning single entry dictionaries here since it pages for each new identifier
                        row.countries[row2.id.split('~')[0]] = row2.metadata['Country-Series']
                except:
                    pass

        if time:
            row.time = {}
            n = 0
            while n < len(time):
                st = ';'.join(['{}~{}'.format(row.id,elem) for elem in time[n:n+pg_size]])
                n += pg_size
                url2 = '{}/{}/sources/{}/Series-Time/{}/metadata'.format(w.endpoint, w.lang, db, st)

                try:
                    for row2 in w.metadata(url2):
                        row.time[row2.id.split('~')[1]] = row2.metadata['Series-Time']
                except:
                    pass

        yield row


def get(id,countries=[],time=[],db=None):
    
    for row in fetch(id, countries, time, db):
        return row
