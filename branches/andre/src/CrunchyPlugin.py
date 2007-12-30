"""
The crunchy plugin API
"""
import threading
from os.path import dirname
from imp import find_module
import random

import src.vlam as vlam
import src.cometIO as cometIO
import src.PluginServices as services

# Rather than having plugins import ElementTree if needed, we will expose
# the required API through CrunchyPlugin.  This way, if we ever
# use something else than ElementTree, we can avoid having to change
# any working plugin, as long as we maintain the API here.

from src.interface import Element, SubElement, fromstring, tostring, parse, \
                          plugin, server
plugin['services'] = services

# We generate a random string that will be appended to javascript functions
# (like /exec and /doctest) used to communicate with the Python server.
session_random_id = str(int(random.random()*1000000000)) + str(
                                           int(random.random()*1000000000))
plugin['session_random_id'] = session_random_id

DEBUG = False

def register_http_handler(pattern, handler):
    """Register a new http handler, see http_serve.py for documentation on
    the request object passed to http handlers."""
    if DEBUG:
        print("Registering http handler " + pattern)
    if pattern is None:
        server['server'].register_default_handler(handler)
    else:
        server['server'].register_handler(pattern, handler)
        pass
plugin['register_http_handler'] = register_http_handler

def register_tag_handler(tag, attribute, keyword, handler):
    """register a new tag handler, a generalisation of vlam handlers
       but for attributes other than 'title'."""
    if keyword is None:
        if attribute is None:  # example: for <a ...>
            if tag in vlam.CrunchyPage.handlers1:
                print ("""FATAL ERROR
Attempting to define a null handler twice for the same
tag: %s
Handlers should be unique: a new plugin must have been"
created, that conflicts with an existing one."""%tag)
                raise
            else:
                vlam.CrunchyPage.handlers1[tag] = handler
                return
        else:   # example "no_tag" (for default menu), with attribute "name"
            if tag not in vlam.CrunchyPage.handlers2:
                vlam.CrunchyPage.handlers2[tag] = {}
                vlam.CrunchyPage.handlers2[tag][attribute] = handler
                return
            elif attribute not in vlam.CrunchyPage.handlers2[tag]:
                vlam.CrunchyPage.handlers2[tag][attribute] = handler
                return
            else:
                print("""FATAL ERROR"
Attempting to define a handler twice for the same combination
tag: %s, attribute: %s
Handlers should be unique: a new plugin must have been
created, that conflicts with an existing one."""%(tag, attribute))
                raise
    # Dealing with case where tag, attribut and keyword are all defined.
    if tag not in vlam.CrunchyPage.handlers3:
        vlam.CrunchyPage.handlers3[tag] = {}
    if attribute not in vlam.CrunchyPage.handlers3[tag]:
        vlam.CrunchyPage.handlers3[tag][attribute] = {}
    if keyword in vlam.CrunchyPage.handlers3[tag][attribute]:
        print("""FATAL ERROR"
Attempting to define a handler twice for the same
tag: %s, attribute: %s, keyword: %s
Handlers should be unique: a new plugin must have been
created, that conflicts with an existing one."""%(tag, attribute, keyword))
        #raise   # ignore for now...
    vlam.CrunchyPage.handlers3[tag][attribute][keyword] = handler
    return
plugin['register_tag_handler'] = register_tag_handler

def register_page_handler(handler):
    """register a callback that is called when each page is created"""
    vlam.CrunchyPage.pagehandlers.append(handler)
plugin['register_page_handler'] = register_page_handler

def create_vlam_page(filehandle, url, remote=False, local=False):
    """Create (and return) a VLAM page from filehandle"""
    return vlam.CrunchyPage(filehandle, url, remote=remote, local=local)
plugin['create_vlam_page'] = create_vlam_page

def exec_code(code, uid, doctest=False):
    """execute some code in a given uid"""
    cometIO.do_exec(code, uid, doctest=doctest)
plugin['exec_code'] = exec_code

def register_service(function, servicename):
    """Register a new service, takes a callable object.
    Once a service is registered it will be available to all plugins by calling
    CrunchyPlugin.servicename()
    """
    setattr(services, servicename, function)
plugin['register_service'] = register_service

def exec_js(pageid, jscode):
    """execute some javascript in the page (NB: this is done asynchronously)"""
    cometIO.write_js(pageid, jscode)
plugin['exec_js'] = exec_js

# The following function appears to not be used anywhere else
def append_html(page_id, output_id, htmlcode):
    """append some html to an IO widget"""
    cometIO.write_output(page_id, output_id, htmlcode)
plugin['append_html'] = append_html

def get_pageid():
    """when executed from inside a 'user thread', returns the pageid of the page
    from which the code is being executed.
    """
    return threading.currentThread().getName().split(":")[0]
plugin['get_pageid'] = get_pageid

def get_uid():
    """when executed from inside a 'user thread', returns the uid of the widget
    from which the code is being executed.
    """
    return threading.currentThread().getName()
plugin['get_uid'] = get_uid

def get_root_dir():
    """return the data directory used by the current crunchy install,
    for now this is always the crunchy base directory
    """
    return dirname(find_module("crunchy")[1])
plugin['get_root_dir'] = get_root_dir

def gen_uid():
    return vlam.uidgen()
plugin['gen_uid'] = gen_uid
