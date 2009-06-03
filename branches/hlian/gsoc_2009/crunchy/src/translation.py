"""
translation.py
Translation infrastructure for Crunchy.
"""

import codecs
import os.path
from imp import find_module

from src.interface import u_print, crunchy_bytes

current_locale = None
DEBUG = False

# adapted from the old Crunchy (pre 0.7)
_selected = {}
languages = {}

def init_translation(lang='en'):
    '''Selects the translation corresponding to the language code and
       returns it. Builds the language dictionary out of the gettext
       file if it is not already loaded.'''

    global _selected
    if lang not in languages:
        paths = os.path
        trans_path = paths.join(paths.dirname(__file__),
                                '..',
                                "translations")
        trans_path = paths.normpath(trans_path)
        filename = paths.join(trans_path,
                              'en',
                              'LC_MESSAGES',
                              'crunchy.po')
        try:
            languages[lang] = build_dict(filename)
        except IOError:
            _selected = {}
        else:
            _selected = languages[lang]
    else:
        _selected = languages[lang]

    if DEBUG:
        import pprint
        pprint.pprint(_selected)

def _(message):
    ''' translate a message, taking care of encoding issues if needed.'''
    global _selected
    message = message.replace("\n","")
    if message in _selected:
        return _selected[message]
    else:
        # Since most of the crunchy code is encoded in UTF-8, we will
        # assume the message key is UTF-8 in order to ensure that _
        # always returns Unicode.
        if isinstance(message, crunchy_bytes):
            message = message.decode('utf8')
        return message # returns untranslated one as default

def build_dict(filename):
    """This function creates a Python dict from a simple standard .po file."""
    global _language_file_encoding
    # currently (January 2007), both language files (English and French)
    # have been set up in poedit with utf-8 as the default encoding.
    # In the future, as other languages are added by contributors,
    # we might want to extract the real encoding used instead of assuming
    # it is utf-8.
    _language_file_encoding = "utf-8"
    translation = {}

    try:
        lines = codecs.open(filename, 'r',
                            _language_file_encoding).readlines()
    except IOError:
        u_print("In translation.py's build_dict, could not open file = ", filename)
        raise

    header = True
    msgid = False
    msgstr = False
    for line in lines:
        if header:       # may need to be adapted to extract the information
            if line.startswith("#"): header = False # from the .po file
        else:
            if line.startswith("msgid "):
                msgid = True
                key = line[7:-2]  # strips extra quotes and newline character
                                  # as well as the "msgid " identifier
            elif line.startswith("msgstr "):
                msgstr = True
                msgid = False
                value = line[8:-2]
            elif line.startswith('"') or line.startswith("'"):
                if msgid:
                    key += line[1:-2]
                elif msgstr:
                    value += line[1:-2]
            elif line.startswith("\n"):
                key = key.replace("\\n","")
                value = value.replace("\\n", "\n")
                translation[key] = value
                msgid = False
                msgstr = False
    return translation
