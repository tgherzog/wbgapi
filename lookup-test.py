
# this script tests the country name lookup module against several
# common country lists to test results

import wbgapi as wb
from pyquery import PyQuery

def report(url, names):

    print('\nResults for {}\n'.format(url))
    wb.economy.coder.report(wb.economy.coder.lookup(names))

# scrape a list of UN member states
member_names = []
url = 'https://www.un.org/en/member-states/'
doc = PyQuery(url, verify=False)
for elem in doc('span.member-state-name'):
    if len(elem.text):
        member_names.append(elem.text)

report(url, member_names)

# IBRD Membership
ibrd_names = []
url = 'https://www.worldbank.org/en/about/leadership/members'
doc = PyQuery(url)
for elem in doc('.tabcontent0 b'):
    if elem.text:
        ibrd_names.append(elem.text)

report(url, ibrd_names)


# Brittanica
url = 'https://www.britannica.com/topic/list-of-countries-1993160'
doc = PyQuery(url)
brit_names = []
for elem in doc('section li a'):
    if elem.text:
        brit_names.append(elem.text)

report(url, brit_names)

# Countries of the World
url = 'https://www.countries-ofthe-world.com/all-countries.html'
doc = PyQuery(url, headers={'user-agent': 'Mozilla'})
cow_names = []
for elem in doc('#content .list-container li'):
    if len(elem.text) > 1:
        cow_names.append(elem.text)

report(url, cow_names)

# DFA
url = 'https://www.dfa.ie/travel/travel-advice/a-z-list-of-countries/'
doc = PyQuery(url)
dfa_names = []
for elem in doc('#countriesbox a'):
    dfa_names.append(elem.text)

report(url, dfa_names)
