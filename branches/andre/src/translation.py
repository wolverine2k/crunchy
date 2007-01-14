# translation.py

# Note: the base directory is called "crunchy_locale" instead of "locale".

import os
import sys

home = None # home is defined properly in preferences

english = {}
french = {}
_editarea_lang = 'en' # default
_system_encoding = sys.getdefaultencoding()
current_page_encoding = None  # obtained from crunchyfier.py as of Jan. 2007

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
    ''' translate a message, taking care of encoding issues if needed.'''
    global _language_file_encoding
    message = message.replace("\n","")  # message is a key in a dict
    if message in _selected:
        if current_page_encoding == _language_file_encoding:
            return _selected[message]
        else:
    # Note: _selected[] has already been decoded from _language_file_encoding
            return _selected[message].encode(current_page_encoding)
    else:
        return message # returns untranslated one as default

def build_dict(filename):
    global _language_file_encoding
    translation = {}
    """This function creates a Python dict from a simple standard .po file."""
    lines = open(filename).readlines()
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

def translate_path(path):
    '''
       When a path is obtained from an <input type='file'>, it is encoded
       according to the html page settings.  When the file is retrieved
       from the local system, it is assumed to be encoded according to the 
       default system encoding.  This function changes the encoding
       appropriately if required.
    '''
    if current_page_encoding == _system_encoding:
        return path
    return path.decode(current_page_encoding).encode(_system_encoding)
