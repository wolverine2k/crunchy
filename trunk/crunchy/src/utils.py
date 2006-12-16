"""Various Utilities"""

__next = 0

    
def next_luid():
    """Returns an LUID as a string"""
    global __next
    __next += 1
    return str(__next)

def html_escape(string):
    """returns string with some characters ecaped, safe for embedding in html"""
    string = string.replace('&', '&amp;')
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    return string