"""session.py
Keeps track of all the data for each session.
A session consists of a set of pages, indexed by UIDs and pathnames.

Everything in here is thread-safe - you won't have to lock anything when using this.
"""

# once we have initialised there is only 1 global (and empty) session:
session = {}

# we should never access session directly, but instead we should use
# the helper functions provided:
def add_page(pageid, page):
    """add_page() expects a string pageid and a vlam page object"""
    session[pageid] = page
    
def write_to(pageid, uid, data, ty):
    """write some data to the page,
    ty is a string, one of the Crunchy COMET datatypes
    """
    pass
    
def read_from(pageid):
    """block until data can be read, then return that data
    data will be in the crunchy COMET format
    """
    pass
    
def get_page(pageid):
    """returns the page data as a string"""
    pass
