'''built in pages in crunchy'''

from urllib2 import urlopen
from urllib import pathname2url

import httprepl
import crunchytute
import widget_javascript

# The following variables are initialised in crunchy.py
repl = None    # read-eval-print-loop: Python interpreter
server = None
import preferences
prefs = preferences.UserPreferences()

def get_index(dummy):
    '''Default page displayed to user.'''
    # In future version, a choice might be given as to which file
    # is loaded based on the language.
    return open(prefs.home).read()

def get_exit(dummy):
    """
    Firefox does not allow a Window to be closed using javascript unless it
    had been opened by a javascript script.  So, we fool it by "reopening" a
    window within it via a script, and close this "new" window.
    Internet Explorer will ask for a confirmation to close the window.
    """
    server.still_serving = False
    return """
    <html><head><script language="javascript" type="text/javascript">
        function closeWindow() {
            window.open('','_parent','');
            window.close();
        }
        closeWindow();
    </script></head></html>"""

def get_push(args):
    '''the push part of the ajax interpreter, uses POST
    '''
    result = httprepl.interps[args['name']].push(args["line"])
    if result is None: 
        return 204
    return result

def get_dir(args):
    '''the dir part of the ajax interpreter, uses GET
    '''
    result = httprepl.interps[args['name']].dir(args["line"])
    if result == None: 
        return 204
    else:
        #have to convert the list to a string
        result = repr(result)
    return result

def get_doc(args):
    '''the doc part of the ajax interpreter, uses GET
    '''
    result = httprepl.interps[args['name']].doc(args["line"])
    if not result: 
        return 204
    return result

def get_external_page(args):
    """load an external page into crunchy"""
    try:
        handle = urlopen(args['path'])
    except:
        return 404
    vlam = crunchytute.VLAMPage(handle, args['path'], True)
    return vlam.get()

def get_local_page(args):
    """load an arbitrary local page into crunchy"""
    path = pathname2url(args['path'])
    try:
        handle = urlopen('file://' + path)
    except:
        return 404
    vlam = crunchytute.VLAMPage(handle, 'file://' + path, True)
    return vlam.get()

def get_user_js(args):
    """loads a user-constructed javascript into crunchy"""
    path = args['path']
    try:
        handle = urlopen('file://' + path)
    except:
        return 404
    return handle.read()

def get_language(args):
    prefs.language = args['language']
    handle = open(prefs.options)
    vlam = crunchytute.VLAMPage(handle, prefs.options)
    return vlam.get()

def get_editor_js(args):
    return widget_javascript.editor

def get_common_js(args):
    return widget_javascript.common

def get_interpreter_js(args):
    return widget_javascript.interpreter