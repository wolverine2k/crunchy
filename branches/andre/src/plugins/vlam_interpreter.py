"""  Crunchy interpreter plugin.

From some Python code simulating a Python interpreter session
contained inside a <pre> element, it inserts an actual interpreter
for user interaction.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

import copy
import sys

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, translate, tostring
import src.utilities as utilities
import src.plugins.colourize as colourize

_ = translate['_']

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
    plugin['register_tag_handler']("pre", "title", "interpreter", insert_interpreter)
    plugin['register_tag_handler']("pre", "title", "isolated", insert_interpreter)
    # just for fun, we define these; they are case-sensitive.
    plugin['register_tag_handler']("pre", "title", "Borg", insert_interpreter)
    plugin['register_tag_handler']("pre", "title", "Human", insert_interpreter)
    plugin['register_tag_handler']("pre", "title", "parrot", insert_interpreter)
    plugin['register_tag_handler']("pre", "title", "Parrots", insert_interpreter)
    plugin['register_tag_handler']("pre", "title", "TypeInfoConsole", insert_interpreter)
    plugin['register_tag_handler']("pre", "title", "python_tutorial", insert_interpreter)
#  Unfortunately, IPython interferes with Crunchy; I'm commenting it out, keeping it in as a reference.
##    plugin['register_tag_handler']("pre", "title", "ipython", insert_interpreter)


def insert_interpreter(page, elem, uid):
    """inserts an interpreter (and the js code to initialise an interpreter)"""

    # First, some definitions that need to be made as local variables
    # since they will use a local variable, pageid
    prefix = config['_prefix']
    crunchy_help = _("Type %s.help for more information."%prefix)

    BorgInterpreter_js = r"""
    function init_BorgInterpreter(uid){
        code = "import src.configuration as configuration\n";
        code += "locals = {'%s': configuration.defaults}\n";
        code += "import src.interpreter\nborg=src.interpreter.BorgConsole(locals, group='%s')";
        code += "\nborg.push('print(";
        code += '"Crunchy: Borg Interpreter (Python version %s). %s"';
        code += ")')\nborg.interact()\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """%(prefix, page.pageid, (sys.version.split(" ")[0]), crunchy_help,
               plugin['session_random_id'])

    SingleInterpreter_js = r"""
    function init_SingleInterpreter(uid){
        code = "import src.configuration as configuration\n";
        code += "locals = {'%s': configuration.defaults}\n";
        code += "import src.interpreter\nisolated=src.interpreter.SingleConsole(locals)";
        code += "\nisolated.push('print(";
        code += '"Crunchy: Individual Interpreter (Python version %s)."';
        code += ")')\nisolated.interact(ps1='--> ')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """%(prefix, (sys.version.split(" ")[0]), plugin['session_random_id'])

    parrot_js = r"""
    function init_parrotInterpreter(uid){
        code = "import src.configuration as configuration\n";
        code += "locals = {'%s': configuration.defaults}\n";
        code += "import src.interpreter\nisolated=src.interpreter.SingleConsole(locals)";
        code += "\nisolated.push('print(";
        code += '"Crunchy: [dead] parrot Interpreter (Python version %s)."';
        code += ")')\nisolated.interact(ps1='_u__) ', symbol='exec')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """%(prefix, (sys.version.split(" ")[0]), plugin['session_random_id'])

    Parrots_js = r"""
    function init_ParrotsInterpreter(uid){
        code = "import src.configuration as configuration\n";
        code += "locals = {'%s': configuration.defaults}\n";
        code += "import src.interpreter\nborg=src.interpreter.BorgConsole(locals, group='%s')";
        code += "\nborg.push('print(";
        code += '"Crunchy: [dead] Parrots Interpreter (Python version %s)."';
        code += ")')\nborg.interact(ps1='_u__)) ', symbol='exec')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """%(prefix, page.pageid, (sys.version.split(" ")[0]), plugin['session_random_id'])

    TypeInfoConsole_js = r"""
    function init_TypeInfoConsole(uid){
        code = "import src.configuration as configuration\n";
        code += "locals = {'%s': configuration.defaults}\n";
        code += "import src.interpreter\nborg=src.interpreter.TypeInfoConsole(locals, group='%s')";
        code += "\nborg.push('print(";
        code += '"Crunchy: TypeInfoConsole (Python version %s)."';
        code += ")')\nborg.interact(ps1='<t>>> ')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """%(prefix, page.pageid, (sys.version.split(" ")[0]), plugin['session_random_id'])

    #
    # We are now ready to proceed with the actual code.

    vlam = elem.attrib["title"]
    c = config['override_default_interpreter']
    if c == 'default':
        # go with interpreter specified in tutorial
        if "isolated" in vlam or "Human" in vlam:
            interp_kind = "isolated"
        elif 'parrot' in vlam:
            interp_kind = 'parrot'
        elif 'Parrots' in vlam:
            interp_kind = "Parrots"
        elif 'TypeInfoConsole' in vlam:
            interp_kind = "TypeInfoConsole"
    #  Unfortunately, IPython interferes with Crunchy; I'm commenting it out, keeping it in as a reference.
    ##    elif "ipython" in vlam:
    ##        interp_kind = "ipython"
        elif 'python_tutorial' in vlam:
            text = colourize.extract_code(elem, trim=True)
            if text.startswith(">>>") or text.startswith("&gt;&gt;&gt;"):
                interp_kind = 'borg'
            else:
                return   # assume it is not an interpreter session.
        else:
            interp_kind = "borg"
    else:
        if c == "isolated" or c == "Human":
            interp_kind = "isolated"
        elif c == 'parrot':
            interp_kind = 'parrot'
        elif c == 'Parrots':
            interp_kind = "Parrots"
        elif 'TypeInfoConsole' in vlam:
            interp_kind = "TypeInfoConsole"
    #  Unfortunately, IPython interferes with Crunchy; I'm commenting it out, keeping it in as a reference.
    ##    elif "ipython" in vlam:
    ##        interp_kind = "ipython"
        else:
            interp_kind = "borg"

    log_id = utilities.extract_log_id(vlam)
    if log_id:
        t = 'interpreter'
        config['logging_uids'][uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config['page_security_level'](page.url):
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
        elif interp_kind == "parrot":
            if not page.includes("parrot_included"):
                page.add_include("parrot_included")
                page.add_js_code(parrot_js)
            page.add_js_code('init_parrotInterpreter("%s");' % uid)
        elif interp_kind == "Parrots":
            if not page.includes("Parrots_included"):
                page.add_include("Parrots_included")
                page.add_js_code(Parrots_js)
            page.add_js_code('init_ParrotsInterpreter("%s");' % uid)
        elif interp_kind == "TypeInfoConsole":
            if not page.includes("TypeInfoConsole_included"):
                page.add_include("TypeInfoConsole_included")
                page.add_js_code(TypeInfoConsole_js)
            page.add_js_code('init_TypeInfoConsole("%s");' % uid)
#  Unfortunately, IPython interferes with Crunchy; I'm commenting it out, keeping it in as a reference.
##        else:
##          if not page.includes("IPythonInterpreter_included"):
##              page.add_include("IPythonInterpreter_included")
##              page.add_js_code(IPythonInterpreter_js)
##          page.add_js_code('init_IPythonInterpreter("%s");' % uid)
    # then we can go ahead and add html markup, extracting the Python
    # code to be executed in the process - we will not need this code;
    # this could change in a future version where we could add a button to
    # have the code automatically "injected" and executed by the
    # interpreter, thus saving some typing by the user.
    code, markup, error = plugin['services'].style_pycode(page, elem)
    if log_id:
        config['log'][log_id] = [tostring(markup)]
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_pycode() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = "crunchy"
    code += "\n"
    if not "no-pre" in vlam:
        try:
            elem.insert(0, markup)
        except AssertionError:
            pass
    plugin['services'].insert_io_subwidget(page, elem, uid,
                        interp_kind = interp_kind, sample_code = code)
    plugin['services'].insert_tooltip(page, elem, uid)
    return


#  Unfortunately, IPython interferes with Crunchy; I'm commenting it out, keeping it in as a reference.

##IPythonInterpreter_js = r"""
##function init_IPythonInterpreter(uid){
##    code = "import src.configuration as configuration\n";
##    code += "locals = {'%s': configuration.defaults}\n";
##    code += "import src.interpreter\n";
##    code += "isolated=src.interpreter.SingleConsole(locals)\n";
##    code += "isolated.push('print(";
##    code += '"Crunchy: Attempting to load IPython shell"';
##    code += ")')\n";
##    code += "isolated.push('from IPython.Shell import IPShellEmbed')\n";
##    code += "isolated.push('from IPython.Release import version as IPythonVersion')\n";
##    code += "isolated.push('" + 'ipshell = IPShellEmbed(["-colors", "NoColor"],';
##    code += '  banner="Crunchy IPython (Python version %s, IPython version %%s)"%%(';
##    code += "  IPythonVersion))')\n";
##    code += "isolated.push('ipshell()')\n";
##    var j = new XMLHttpRequest();
##    j.open("POST", "/exec%s?uid="+uid, false);
##    j.send(code);
##};
##"""%(prefix, sys.version.split(" ")[0], plugin['session_random_id'])
