"""The demo crunchy plugin API
"""

import vlam
import cometIO

class CrunchyPlugin(object):
    """All Plugins inherit CrunchyPlugin, the various member functions
    make up the plugin API"""
    server = None
    def __init__(self):
        """Plugins (ie. subclasses) must not override this.
        Performs all general plugin initialisation."""
        self.register()
        
    def register(self):
        """Plugins must override this to perform all plugin-specific initialisation."""
        raise NotImplementedError
    
    def register_http_handler(self, pattern, handler):
        """Register a new http handler"""
        if pattern is None:
            CrunchyPlugin.server.register_default_handler(handler)
        else:
            CrunchyPlugin.server.register_handler(handler, pattern)
            pass
        
    def register_vlam_handler(self, elem_type, option, handler):
        """register a new vlam handler"""
        if elem_type not in vlam.CrunchyPage.handlers:
            vlam.CrunchyPage.handlers[elem_type] = {}
        vlam.CrunchyPage.handlers[elem_type][option] = handler
        pass
    
    def create_vlam_page(self, filehandle):
        """Create (and return) a VLAM page from filehandle"""
        return vlam.CrunchyPage(filehandle)
    
    def exec_code(self, code, uid):
        """execute some code in a given uid"""
        cometIO.do_exec(code, uid)
        
    def register_service(self, function):
        """Register a new service, takes a callable object.
        Once a service is registered it will be available to all plugins by calling
        self.service_name(), where service_name = function.__name__
        """
        setattr(CrunchyPlugin, function.__name__, function)