# translation.py

# Note: the base directory is called "crunchy_locale" instead of "locale".
# If a directory named "locale" exists, wxPython assumes it uses the
# standard 'gettext' approach and expects some standard functions to
# be defined - which they are not in this customized version.

import os

home = None # home is defined properly in preferences

english = {}
french = {}
_editarea_lang = 'en' # default

def select(lang):
    global _selected, _editarea_lang
    global english, french
    
    print "selected language in translation.py is :", lang
    if lang in ['en', 'fr', 'pt', 'pl', 'ja', 'it', 'dk', 'de']:
        _editarea_lang = lang
    else:
        _editarea_lang = 'en'
    
    if lang == 'fr':
        if french == {}:
            filename = os.path.join(home, "crunchy_locale", "fr", "french.po")
            french = build_dict(filename)
        _selected = french
    else: # English is the default
        if english == {}:
            filename = os.path.join(home, "crunchy_locale", "en", "english.po")
            english = build_dict(filename)
        _selected = english


def get_editarea_lang():
    global _editarea_lang
    return _editarea_lang

def _(message):
    message = message.replace("\n","")  # message is a key in a dict
    if message in _selected:
        return _selected[message]
    else:
        return message # returns untranslated one as default

def build_dict(filename):
    translation = {}
    """This function creates a Python dict from a simple standard .po file."""
    lines = open(filename).readlines()
    header = True
    msgid = False
    msgstr = False
    for line in lines:
        line = line.decode("utf-8") # encoding that was chosen with poedit;
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
