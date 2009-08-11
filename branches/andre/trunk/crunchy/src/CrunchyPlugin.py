"""
The crunchy plugin API
"""
import threading
from os.path import dirname
import random

import src.vlam as vlam
import src.cometIO as cometIO
import src.PluginServices as services

# Rather than having plugins import ElementTree if needed, we will expose
# the required API through CrunchyPlugin.  This way, if we ever
# use something else than ElementTree, we can avoid having to change
# any working plugin, as long as we maintain the API here.

from src.interface import plugin, server, preprocessor, additional_vlam
plugin['services'] = services

# We generate a random string that will be appended to javascript functions
# (like /exec and /doctest) used to communicate with the Python server.
session_random_id = str(int(random.random()*1000000000)) + str(
                                           int(random.random()*1000000000))
plugin['session_random_id'] = session_random_id

DEBUG = False

def add_vlam_option(option_name, *args):
    '''records an additional vlam argument requested by a plugin to be
       added to an existing vlam option'''
    for arg in args:
        additional_vlam.setdefault(option_name, []).append(arg)
plugin['add_vlam_option'] = add_vlam_option

def register_http_handler(pattern, handler):
    """Register a new http handler, see http_serve.py for documentation on
    the request object passed to http handlers."""
    if DEBUG:
        print("Registering http handler " + pattern)
    if pattern is None:
        server['server'].register_default_handler(handler)
    else:
        server['server'].register_handler(pattern, handler)

plugin['register_http_handler'] = register_http_handler

def register_preprocessor(extension, handler):
    '''register a handler used to preprocess a file, based on a
       registered extension, prior to creating a vlam page from it.'''
    preprocessor[extension] = handler
    return
plugin['register_preprocessor'] = register_preprocessor

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

def register_begin_tag_handler(tag, handler):
    vlam.CrunchyPage.begin_handlers1[tag] = handler
plugin['register_begin_tag_handler'] = register_begin_tag_handler

def register_final_tag_handler(tag, handler):
    vlam.CrunchyPage.final_handlers1[tag] = handler
plugin['register_final_tag_handler'] = register_final_tag_handler

def register_begin_pagehandler(handler):
    """register a callback that is called when each page is created,
       as part of the first processing steps of that page.
    """
    vlam.CrunchyPage.begin_pagehandlers.append(handler)
plugin['register_begin_pagehandler'] = register_begin_pagehandler

def register_end_pagehandler(handler):
    """register a callback that is called when each page is created,
       as part of the last processing steps of that page.
    """
    vlam.CrunchyPage.end_pagehandlers.append(handler)
plugin['register_end_pagehandler'] = register_end_pagehandler

def create_vlam_page(filehandle, url, username=None, remote=False, local=False):
    """Create (and return) a VLAM page from filehandle"""
    return vlam.CrunchyPage(filehandle, url, username=username,
                                                    remote=remote, local=local)
plugin['create_vlam_page'] = create_vlam_page

def exec_code(code, uid, doctest=False):
    """execute some code in a given uid"""
    cometIO.do_exec(code, uid, doctest=doctest)
plugin['exec_code'] = exec_code

def register_service(servicename, function):
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

def append_text(page_id, output_id, text):
    """append some text to an IO widget on an html page."""
    cometIO.write_output(page_id, output_id, text)
plugin['append_text'] = append_text

def get_pageid():
    """when executed from inside a 'user thread', returns the pageid of the page
    from which the code is being executed.
    """
    return threading.currentThread().getName().split("_")[0]
plugin['get_pageid'] = get_pageid

def get_uid():
    """when executed from inside a 'user thread', returns the uid of the widget
    from which the code is being executed.
    """
    return threading.currentThread().getName()
plugin['get_uid'] = get_uid

def kill_thread(uid):
    """kill a thread, given its assocated uid"""
    cometIO.kill_thread(uid)
plugin['kill_thread'] = kill_thread
