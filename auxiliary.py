
# ancillary and deprecated code. Not currently included in the implementation

# Here's an object-oriented approach we may use someday, but I'm not sure it's especially practical
# to implement from region, lendingtype or incomelevel, update list() and get() to yield or return
# Region(row) instead of row

class Region(dict):
    @property
    def members(self):
        return members(self['code'])

