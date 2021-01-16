
import re

def qget(q):
    '''Returns the lower-case search string from text along with possible options. This is used internally

       None or empty string returns None

       A leading '!' is interpreted as a request to search the complete string. In most cases
       this is ignored, but for series, it includes the ending parenethical part of the search which
       is omitted by default.

    Examples:
        q,type = qget()
        q,_    = qget()    # if you don't care about the flag
        q      = qget()[0] # likewise

    Notes:
        If full search doesn't apply, you should ignore the flag returned from qget and pass the default
        option to qmatch. This makes for efficient searching.
    '''

    if q:
        q = q.lower()
        if q[0] == '!':
            return q[1:], True

        return q, False

    return None, False

qmatch_expr = None

def qmatch(q, text, fullSearch=True):

    if q is None:
        return True

    if fullSearch:
        return q in text.lower()

    # otherwise, we remove any ending parenthetical component from the search string
    global qmatch_expr
    if qmatch_expr is None:
        qmatch_expr = re.compile('(.+?)\\s*\\([^)]+?\\)\\s*$')

    m = qmatch_expr.match(text)
    if m:
        text = m.group(1)

    return q in text.lower()

