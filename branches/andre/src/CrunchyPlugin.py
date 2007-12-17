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
import src.translation as translation

# Rather than having plugins import ElementTree if needed, we will expose
# the required API through CrunchyPlugin.  This way, if we ever
# use something else than ElementTree, we can avoid having to change
# any working plugin, as long as we maintain the API here.

#from src.element_tree import ElementTree, HTMLTreeBuilder
#Element = ElementTree.Element
#SubElement = ElementTree.SubElement
#fromstring = ElementTree.fromstring
#tostring = ElementTree.tostring
#parse = HTMLTreeBuilder.parse

from src.universal import Element, SubElement, fromstring, tostring, parse

# We generate a random string that will be appended to javascript functions
# (like /exec and /doctest) used to communicate with the Python server.
session_random_id = str(int(random.random()*1000000000)) + str(
                                           int(random.random()*1000000000))

_ = translation._
DEBUG = False

def register_http_handler(pattern, handler):
    """Register a new http handler, see http_serve.py for documentation on
    the request object passed to http handlers."""
    if DEBUG:
        print("Registering http handler " + pattern)
    if pattern is None:
        server.register_default_handler(handler)
    else:
        server.register_handler(pattern, handler)
        pass

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
tag: %s, option: %s
Handlers should be unique: a new plugin must have been
created, that conflicts with an existing one."""%(elem_type, option))
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

def register_page_handler(handler):
    """register a callback that is called when each page is created"""
    vlam.CrunchyPage.pagehandlers.append(handler)

def create_vlam_page(filehandle, url, remote=False, local=False):
    """Create (and return) a VLAM page from filehandle"""
    return vlam.CrunchyPage(filehandle, url, remote=remote, local=local)

def exec_code(code, uid, doctest=False):
    """execute some code in a given uid"""
    cometIO.do_exec(code, uid, doctest=doctest)

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
