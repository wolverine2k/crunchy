"""This plugin provides tooltips for interpreters"""

import re
import urllib

import src.interpreter as interpreter
# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, translate, plugin, Element, names
_ = translate['_']

borg_console = {}

provides = set(["/dir", "/doc"])

def register():
    '''registers two services and two http handlers: /dir and /doc'''
    plugin['register_service']("insert_tooltip", insert_tooltip)
    plugin['register_http_handler']("/dir%s" % plugin['session_random_id'],
                                    dir_handler)
    plugin['register_http_handler']("/doc%s" % plugin['session_random_id'],
                                    doc_handler)

def insert_tooltip(page, *dummy):
    '''inserts a (hidden) tooltip object in a page'''
    if not page.includes("tooltip_included") and page.body:
        borg_console[page.pageid] = interpreter.BorgConsole(group=page.pageid)

        page.add_include("tooltip_included")
        page.insert_js_file(u"/javascript/tooltip.js")
        page.add_js_code(tooltip_js)

        tooltip = Element("div")
        tooltip.attrib["id"] = u"interp_tooltip"
        tooltip.text = u" "
        page.body.append(tooltip)

        help_menu = Element("div")
        help_menu.attrib["id"] = u"help_menu"
        help_menu.text = u" "
        page.body.append(help_menu)

        help_menu_x = Element("div")
        help_menu_x.attrib["id"] = u"help_menu_x"
        help_menu_x.attrib["onclick"] = u"hide_help();"
        help_menu_x.text = u"X"
        page.body.append(help_menu_x)

def dir_handler(request):
    """Examine a partial line and provide attr list of final expr"""

    pageid = request.args['uid'].split("_")[0]
    username = names[pageid]
    if not config[username]['dir_help']:
        request.send_response(204)
        request.end_headers()
        return

    line = re.split(r"\s", urllib.unquote_plus(request.data))[-1].strip()

    # Support lines like "thing.attr" as "thing.", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = ".".join(line.split(".")[:-1])

    try:
        result = eval("dir(%s)" % line, {}, borg_console[pageid].__dict__['locals'])
    except:
        request.send_response(204)
        request.end_headers()
        return
    if type(result) == type([]):
        # strip private variables
        result = [a for a in result if not a.startswith("_")]

    # have to convert the list to a string
    result = repr(result)
    request.send_response(200)
    request.end_headers()
    request.wfile.write(result)
    request.wfile.flush()

def doc_handler(request):
    """Examine a partial line and provide sig+doc of final expr."""

    pageid = request.args['uid'].split("_")[0]
    username = names[pageid]
    if not config[username]['doc_help']:#configuration.defaults.doc_help:
        request.send_response(204)
        request.end_headers()
        return
    line = re.split(r"\s", urllib.unquote_plus(request.data))[-1].strip()

    # Support lines like "func(text" as "func(", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.

    line = "(".join(line.split("(")[:-1])
    _locals = borg_console[pageid].__dict__['locals']
    if line in _locals:
        result = "%s()\n %s" % (line, _locals[line].__doc__)
    elif '__builtins__' in _locals:
        if line in _locals['__builtins__']:
            result = "%s()\n %s" % (line, _locals['__builtins__'][line].__doc__)
        else:
            request.send_response(204)
            request.end_headers()
            return
    else:
        result = _("builtins not defined in console yet.")

    request.send_response(200)
    request.end_headers()
    request.wfile.write(result)
    request.wfile.flush()
    return

# javascript code
tooltip_js = u"""
var session_id = "%s";
""" % plugin['session_random_id']
