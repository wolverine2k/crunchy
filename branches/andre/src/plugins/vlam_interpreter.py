"""  Crunchy interpreter plugin.

From some Python code simulating a Python interpreter session
contained inside a <pre> element, it inserts an actual interpreter
for user interaction.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

import sys

# All plugins should import the crunchy plugin API
import src.CrunchyPlugin as CrunchyPlugin
import src.configuration as configuration
from src.utilities import extract_log_id

# The set of other "widgets/services" required from other plugins
requires = set(["io_widget", "/exec"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register only two type of 'actions':
        a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       """
    # 'interpreter' only appears inside <pre> elements, using the notation
    # <pre title='interpreter ...'>
    CrunchyPlugin.register_tag_handler("pre", "title", "interpreter", insert_interpreter)
    # just for fun, we define these; they are case-sensitive.
    CrunchyPlugin.register_tag_handler("pre", "title", "Borg", insert_interpreter)
    CrunchyPlugin.register_tag_handler("pre", "title", "Human", insert_interpreter)
    # new one for IPython!
    CrunchyPlugin.register_tag_handler("pre", "title", "ipython", insert_interpreter)

def insert_interpreter(page, elem, uid):
    """inserts an interpreter (and the js code to initialise an interpreter)"""
    vlam = elem.attrib["title"]
    if "isolated" in vlam or "Human" in vlam:
        interp_kind = "isolated"
    elif "ipython" in vlam:
        interp_kind = "ipython"
    else:
        interp_kind = "borg"
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'interpreter'
        configuration.defaults.logging_uids[uid] = (log_id, t)

    # first we need to make sure that the required javacript code is in the page:
    if interp_kind == "borg":
        if not page.includes("BorgInterpreter_included"):
            page.add_include("BorgInterpreter_included")
            page.add_js_code(BorgInterpreter_js)
        page.add_js_code('init_BorgInterpreter("%s");' % uid)
    elif interp_kind == "isolated":
        if not page.includes("SingleInterpreter_included"):
            page.add_include("SingleInterpreter_included")
            page.add_js_code(SingleInterpreter_js)
        page.add_js_code('init_SingleInterpreter("%s");' % uid)
    else:
        if not page.includes("IPythonInterpreter_included"):
            page.add_include("IPythonInterpreter_included")
            page.add_js_code(IPythonInterpreter_js)
        page.add_js_code('init_IPythonInterpreter("%s");' % uid)
    # then we can go ahead and add html markup, extracting the Python
    # code to be executed in the process - we will not need this code;
    # this could change in a future version where we could add a button to
    # have the code automatically "injected" and executed by the
    # interpreter, thus saving some typing by the user.
    code, markup = CrunchyPlugin.services.style_pycode(page, elem)
    if log_id:
        configuration.defaults.log[log_id] = [CrunchyPlugin.tostring(markup)]
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_doctest() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.insert(0, markup)
    CrunchyPlugin.services.insert_io_subwidget(page, elem, uid, interp_kind = interp_kind)
    CrunchyPlugin.services.insert_tooltip(page, elem, uid)
    return


prefix = configuration.defaults._prefix
crunchy_help = "Type %s.help for more information."%prefix

BorgInterpreter_js = r"""
function init_BorgInterpreter(uid){
    code = "import src.configuration as configuration\n";
    code += "locals = {'%s': configuration.defaults}\n";
    code += "import src.interpreter\nborg=src.interpreter.BorgConsole(locals)";
    code += "\nborg.push('print ";
    code += '"Crunchy: Borg Interpreter (Python version %s). %s"';
    code += "')\nborg.interact('')\n";
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%s?uid="+uid, false);
    j.send(code);
};
"""%(prefix, (sys.version.split(" ")[0]), crunchy_help,
           CrunchyPlugin.session_random_id)

SingleInterpreter_js = r"""
function init_SingleInterpreter(uid){
    code = "import src.configuration as configuration\n";
    code += "locals = {'%s': configuration.defaults}\n";
    code += "import src.interpreter\nisolated=src.interpreter.SingleConsole(locals)";
    code += "\nisolated.push('print ";
    code += '"Crunchy: Individual Interpreter (Python version %s). %s"';
    code += "')\nisolated.interact('')\n";
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%s?uid="+uid, false);
    j.send(code);
};
"""%(prefix, (sys.version.split(" ")[0]), crunchy_help,
           CrunchyPlugin.session_random_id)

IPythonInterpreter_js = r"""
function init_IPythonInterpreter(uid){
    code = "import src.configuration as configuration\n";
    code += "locals = {'%s': configuration.defaults}\n";
    code += "import src.interpreter\n";
    code += "isolated=src.interpreter.SingleConsole(locals)\n";
    code += "isolated.push('print ";
    code += '"Crunchy: Attempting to load IPython shell"';
    code += "')\n";
    code += "isolated.push('from IPython.Shell import IPShellEmbed')\n";
    code += "isolated.push('from IPython.Release import version as IPythonVersion')\n";
    code += "isolated.push('" + 'ipshell = IPShellEmbed(["-colors", "NoColor"],';
    code += '  banner="Crunchy IPython (Python version %s, IPython version %%s)"%%(';
    code += "  IPythonVersion))')\n";
    code += "isolated.push('ipshell()')\n";
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%s?uid="+uid, false);
    j.send(code);
};
"""%(prefix, sys.version.split(" ")[0], CrunchyPlugin.session_random_id)

##    code += "isolated.push('  print ";
##    code += 'Cannot find IPython; will use normal interpreter instead")'\n;


##IPythonInterpreter_js = r"""
##function init_IPythonInterpreter(uid){
##    code = "import src.configuration as configuration\n";
##    code += "locals = {'%s': configuration.defaults}\n";
##    code += "from IPython.Shell import IPShellEmbed\n";
##    code += "ipshell = IPShellEmbed(user_ns=locals)\n";
##    code += "ipshell()\n";
##    //code += "import src.interpreter\nshell=src.interpreter.IPythonShell(locals)\n";
##    //code += "shell()\n";
##    var j = new XMLHttpRequest();
##    j.open("POST", "/exec%s?uid="+uid, false);
##    j.send(code);
##};
##"""%(prefix, CrunchyPlugin.session_random_id)