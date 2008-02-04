"""This plugin handles all execution requests on /exec, ie. the standard execution method."""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin

# provides and require use the bare name ...
provides = set(["/exec"])

def register():
    '''registers a single http handler: /exec'''
    plugin['register_http_handler']("/exec%s" % plugin['session_random_id'],
                                    exec_handler)

def exec_handler(request):
    """handle an execution request"""
    plugin['exec_code'](request.data, request.args["uid"])
    request.send_response(200)
    request.end_headers()
