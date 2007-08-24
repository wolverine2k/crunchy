"""
translation.py
Translation infrastructure for Crunchy.
"""

import gettext
import os.path
from imp import find_module

current_locale = None
DEBUG = False

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

def _(message):
    global current_locale

    if current_locale is None:
        return message
    return current_locale.gettext(message)
