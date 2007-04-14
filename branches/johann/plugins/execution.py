"""This plugin handles all execution requests on /exec, ie. the standard execution method."""

from CrunchyPlugin import *


def register():
    register_http_handler("/exec", exec_handler)
        
def exec_handler(request):
    """handle an execution request"""
    print "executing..."
    exec_code(request.data, request.args["uid"])