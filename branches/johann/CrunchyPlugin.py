"""
The crunchy plugin API
"""
import threading

import vlam
import cometIO
import PluginServices as services

__all__=["register_http_handler", "register_vlam_handler",
         "create_vlam_page", "exec_code", "register_service", "services",
         "exec_js"]
    
def register_http_handler(pattern, handler):
    """Register a new http handler"""
    if pattern is None:
        server.register_default_handler(handler)
    else:
        server.register_handler(handler, pattern)
        pass
        
def register_vlam_handler(elem_type, option, handler):
    """register a new vlam handler"""
    if elem_type not in vlam.CrunchyPage.handlers:
        vlam.CrunchyPage.handlers[elem_type] = {}
    vlam.CrunchyPage.handlers[elem_type][option] = handler
    
def create_vlam_page(filehandle):
    """Create (and return) a VLAM page from filehandle"""
    return vlam.CrunchyPage(filehandle)
    
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
