"""
translation.py
Translation infrastructure for Crunchy.
"""

import gettext
import os.path
from imp import find_module

current_locale = None

def init_translation(lang=None):
    try:
        if lang:
            try:
                current_locale = gettext.translation("crunchy",
                os.path.join(os.path.dirname(find_module("crunchy")[1]),
                                    "translations/"),languages=[lang])
            except:
                init_translation()
        else:
            current_locale = gettext.translation("crunchy",
            os.path.join(os.path.dirname(find_module("crunchy")[1]),
                                    "translations/"))
    except IOError:
        print "No Language file found, not translating anything"


def _(message):
    global current_locale
    if current_locale is None:
        return message
    return current_locale.lgettext(message)
