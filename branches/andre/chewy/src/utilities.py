'''utilities.py

Contain various function and classes for general use.

fixLineEnding: converts all line endings to '\n'
ThreadStream: class used to redirect stdout and stderr.
'''

import re

def fixLineEnding(txt):
    # Python recognize line endings as '\n' whereas, afaik:
    # Windows uses '\r\n' to identify line endings
    # *nix uses '\n'   (ok :-)
    # Mac OS uses '\r'
    # So, we're going to convert all to '\n'
    txt1 = re.sub('\r\n', '\n', txt) # Windows: tested
    txt = re.sub('\r', '\n', txt1)  # not tested yet: no Mac :-(
    return txt
