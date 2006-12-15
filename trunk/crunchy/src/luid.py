"""Generate Locally Unique IDs (LUIDs), guaranteed to be unique within
this program"""

try:
    __t = __next
except NameError:
    __next = 0
    
def next():
    """Returns an LUID as a string"""
    global __next
    __next += 1
    return str(__next)
