"""
translation.py
Translation infrastructure for Crunchy.
"""

import gettext
import os.path
from imp import find_module

current_locale = None
DEBUG = False

#The following is temporarily replaced by the old Crunchy method
'''
def init_translation(lang=None):
    if DEBUG:
        print "init_translation called with lang=", lang
    try:
        if lang:
            try:
                trans_path = os.path.join(os.path.dirname(
                                    find_module("crunchy")[1]), "translations")
                current_locale = gettext.translation("crunchy", trans_path,
                                                        languages=[lang])
                current_locale.install()
                if DEBUG:
                    print "path to translation files: ", trans_path
                    print "current_locale = ", current_locale
            except:
                if DEBUG:
                    print "exception in init_translation"
                init_translation()
##        else:
##            current_locale = gettext.translation("crunchy",
##            os.path.join(os.path.dirname(find_module("crunchy")[1]),
##                                    "translations"))
    except IOError:
        print "No Language file found, not translating anything"
'''

#The following is temporarily replaced by the old Crunchy method
'''
def _(message):
    global current_locale

    if current_locale is None:
        return message
    return current_locale.gettext(message)
'''


# from the old Crunchy
_selected = {}
english = {}
estonian = {}
french = {}
italian = {}
macedonian = {}
polish = {}


def init_translation(lang=None):
    global english, estonian, french, italian, macedonian, polish, _selected

    trans_path = os.path.join(os.path.dirname(
                                    find_module("crunchy")[1]), "translations")

    if lang == 'et':
        if estonian == {}:
            filename = os.path.join(trans_path, "et", "LC_MESSAGES", "crunchy.po")
            estonian = build_dict(filename)
        _selected = estonian
    elif lang == 'fr':
        if french == {}:
            filename = os.path.join(trans_path, "fr", "LC_MESSAGES", "crunchy.po")
            french = build_dict(filename)
        _selected = french
    elif lang == 'it':
        if italian == {}:
            filename = os.path.join(trans_path, "it", "LC_MESSAGES", "crunchy.po")
            italian = build_dict(filename)
        _selected = italian
    elif lang == 'mk':
        if macedonian == {}:
            filename = os.path.join(trans_path, "mk", "LC_MESSAGES", "crunchy.po")
            macedonian = build_dict(filename)
        _selected = macedonian
    elif lang == 'pl':
        if polish == {}:
            filename = os.path.join(trans_path, "pl", "LC_MESSAGES", "crunchy.po")
            polish = build_dict(filename)
        _selected = polish
    else: # English is the default
        if english == {}:
            filename = os.path.join(trans_path, "en", "LC_MESSAGES", "crunchy.po")
            english = build_dict(filename)
        _selected = english
    if DEBUG:
        import pprint
        pprint.pprint( _selected)

def _(message):
    ''' translate a message, taking care of encoding issues if needed.'''
    global _selected
    message = message.replace("\n","")#.decode("utf-8")
    if message in _selected:
        return _selected[message]
    else:
        return message # returns untranslated one as default

def build_dict(filename):
    global _language_file_encoding
    translation = {}
    """This function creates a Python dict from a simple standard .po file."""
    try:
        lines = open(filename).readlines()
    except:
        print "In translation.py's build_dict, could not open file = ", filename
        return
    header = True
    msgid = False
    msgstr = False
    # currently (January 2007), both language files (English and French)
    # have been set up in poedit with utf-8 as the default encoding.
    # In the future, as other languages are added by contributors,
    # we might want to extract the real encoding used instead of assuming
    # it is utf-8.
    _language_file_encoding = "utf-8"
    for line in lines:
        line = line.decode(_language_file_encoding)
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

