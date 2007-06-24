"""
The crunchy plugin API
"""
import threading
from os.path import dirname
from imp import find_module
import random

import vlam
import cometIO
import PluginServices as services
import translation

__all__=["register_http_handler", "register_vlam_handler",
         "create_vlam_page", "exec_code", "register_service", "services",
         "exec_js", "get_uid", "get_pageid", "get_data_dir", "append_html",
         "gen_uid", "_"]

# We generate a random string that will be appended to javascript functions
# (like /exec and /doctest) used to communicate with the Python server.
session_random_id = str(int(random.random()*1000000000))

_ = translation._

def register_http_handler(pattern, handler):
    """Register a new http handler, see http_serve.py for documentation on
    the request object passed to http handlers."""
    if pattern is None:
        server.register_default_handler(handler)
    else:
        server.register_handler(handler, pattern)
        pass

def register_vlam_handler(elem_type, option, handler):
    """register a new vlam handler, see vlam.py for documentation on the
    page object passed to vlam handlers"""
    if option is None:
        if elem_type in vlam.CrunchyPage.handlers:
            return
        else:
            vlam.CrunchyPage.null_handlers[elem_type] = handler
    if elem_type not in vlam.CrunchyPage.handlers:
        vlam.CrunchyPage.handlers[elem_type] = {}
    vlam.CrunchyPage.handlers[elem_type][option] = handler

def register_page_handler(handler):
    """register a callback that is called when each page is created"""
    vlam.CrunchyPage.pagehandlers.append(handler)

def create_vlam_page(filehandle, url):
    """Create (and return) a VLAM page from filehandle"""
    return vlam.CrunchyPage(filehandle, url)

def exec_code(code, uid):
    """execute some code in a given uid"""
    cometIO.do_exec(code, uid)

def register_service(function, servicename):
    """Register a new service, takes a callable object.
    Once a service is registered it will be available to all plugins by calling
    CrunchyPlugin.servicename()
    """
    setattr(services, servicename, function)

def exec_js(pageid, jscode):
    """execute some javascript in the page (NB: this is done asynchronously)"""
    cometIO.write_js(pageid, jscode)

def append_html(page_id, output_id, htmlcode):
    """append some html to an IO widget"""
    cometIO.write_output(page_id, output_id, htmlcode)
    
def get_pageid():
    """when executed from inside a 'user thread', returns the pageid of the page
    from which the code is being executed.
    """
    return threading.currentThread().getName().split(":")[0]

def get_uid():
    """when executed from inside a 'user thread', returns the uid of the widget
    from which the code is being executed.
    """
    return threading.currentThread().getName()

def get_data_dir():
    """return the data directory used by the current crunchy install,
    for now this is always the crunchy base directory
    """
    return dirname(find_module("crunchy")[1])

def gen_uid():
    return vlam.uidgen()

def get_locale():
    return translation.current_locale
