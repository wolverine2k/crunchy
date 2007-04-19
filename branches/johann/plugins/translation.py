"""translation.py
Translation infrastructure for Crunchy.
"""

import gettext
import os.path

from CrunchyPlugin import *

provides = set(["translation"])

current_locale = None

def register():
    """sets up the localisation system - initialising it to some suitable default"""
    global current_locale
    try:
        current_locale = gettext.translation("crunchy", os.path.join(get_data_dir(), "translations/"))
    except IOError:
        print "No Language file found, not translating anything"
    register_service(_, "_")
    
def _(message):
    global current_locale
    if current_locale is None:
        return message
    return current_locale.lgettext(message)
