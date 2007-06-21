"""This plugin handles all execution requests on /exec, ie. the standard execution method."""

import CrunchyPlugin

# provides and require use the bare name ...
provides = set(["/exec"])

def register():
    # ... whereas we add a random number for security in the actual code used
    CrunchyPlugin.register_http_handler("/exec%s"%CrunchyPlugin.session_random_id, exec_handler)

def exec_handler(request):
    """handle an execution request"""
    CrunchyPlugin.exec_code(request.data, request.args["uid"])
    request.send_response(200)
    request.end_headers()
