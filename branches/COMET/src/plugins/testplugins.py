"""Test plugins for the new demo plugin infrastructure,
Also used in the tutorial at http://code.google.com/p/crunchy/wiki/CrunchyPlugin
"""
from CrunchyPlugin import CrunchyPlugin

class VSP(CrunchyPlugin):
    """A very simple plugin that just loads"""
    def register(self):
        print "A very simple plugin is loading..."
    
class HelloHTTP(CrunchyPlugin):
    """A plugin that overrides /hello"""
    def hello_handler(self, request):
        request.send_response(200)
        request.end_headers()
        request.wfile.write("Hello World!")
        
    def register(self):
        self.register_http_handler("/hello", self.hello_handler)
    
class ServiceTest(CrunchyPlugin):
    """tests the custom service functionality"""
    def register(self):
        self.register_service(ServiceTest.test_service)
        self.register_http_handler("/service_test", self.test_http)
        
    def test_http(self, rq):
        rq.send_response(200)
        rq.end_headers()
        rq.wfile.write(self.test_service({"test_key1":1}))
        
    def test_service(self, arg):
        return str(arg)