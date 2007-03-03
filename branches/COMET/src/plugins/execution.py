"""This plugin handles all execution requests on /exec"""

from CrunchyPlugin import CrunchyPlugin

class ExecPlugin(CrunchyPlugin):
    def register(self):
        self.register_http_handler("/exec", self.handler)
        
    def handler(self, request):
        """handle an execution request"""
        print "executing..."
        self.exec_code(request.data, request.args["uid"])