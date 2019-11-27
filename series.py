
import wbgapi as w

def list():
    url = '{}/{}/sources/{}/series'.format(w.endpoint, w.lang, w.db)

    for row in w.fetch(url):
        yield (row['id'], row['value'])

def get(series, countries='all', time='all', mrv=None, mrnev=None, skipBlanks=False, labels=False, skipAggs=False):

    params = {}
    if mrv:
        params['mrv'] = mrv
    elif mrnev:
        params['mrnev'] = mrnev

    if skipAggs:
        aggs = w.agg_list()

    url = '{}/{}/sources/{}/series/{}/country/{}/time/{}'.format(w.endpoint, w.lang, w.db, w._apiParam(series), w._apiParam(countries), w._apiParam(time))
    for row in w.fetch(url, params):
        if skipBlanks and row['value'] is None:
            continue

        skip = False

        x = {'value': row['value']}
        for elem in row['variable']:
            key = elem['concept'].lower()
            if key == "country" and skipAggs and elem['id'] in aggs:
                skip = True
                break

            if labels:
                del(elem['concept'])
                x[key] = elem
            else:
                x[key] = elem['id']

        if not skip:
            yield x
