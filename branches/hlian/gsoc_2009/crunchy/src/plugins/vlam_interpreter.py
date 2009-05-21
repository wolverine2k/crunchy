"""  Crunchy interpreter plugin.

From some Python code simulating a Python interpreter session
contained inside a <pre> element, it inserts an actual interpreter
for user interaction.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

import sys

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, translate, tostring, Element
import src.utilities as util
import colourize as colourize

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
    interp_kind = ['interpreter', 'Borg', 'isolated', 'Human', 'parrot',
                   'Parrots', 'TypeInfoConsole', 'python_tutorial']
                 #ipython not included as it does not work...
    for interp in interp_kind:
        plugin['register_tag_handler']("pre", "title", interp, insert_interpreter)
        plugin['add_vlam_option']('override_default_interpreter', interp)
        plugin['add_vlam_option']('no_markup', interp)

Python_version = sys.version.split(" ")[0]
titles = {
    'borg': "This is a Borg Interpreter (Python version %s)" % Python_version,
    'interpreter': "This is a Borg Interpreter (Python version %s)" % Python_version,
    'isolated': "This is an isolated Interpreter (Python version %s)" % Python_version,
    'Human': "This is an isolated Interpreter (Python version %s)" % Python_version,
    'parrot': "This is a parrot Interpreter (Python version %s)" % Python_version,
    'Parrots': "This is a Parrots Interpreter (Python version %s)" % Python_version,
    'TypeInfoConsole': "This is a TypeInfoConsole Interpreter (Python version %s)" % Python_version,
}
help_files = {
    'borg': "/docs/popups/borg_interpreter.html",
    'interpreter': "/docs/popups/borg_interpreter.html",
    'isolated': "/docs/popups/isolated_interpreter.html",
    'Human': "/docs/popups/isolated_interpreter.html",
    'parrot': "/docs/popups/parrot_interpreter.html",
    'Parrots': "/docs/popups/parrots_interpreter.html",
    'TypeInfoConsole': "/docs/popups/typeinfoconsole_interpreter.html",
}

for f in help_files:
    help_files[f] += " /docs/popups/keyboard_interrupt.html /docs/popups/editor_image.html"

def insert_interpreter(page, elem, uid):
    """inserts an interpreter (and the js code to initialise an interpreter)"""

    vlam = elem.attrib["title"]
    interp_kind = select_type(vlam,
                    config[page.username]['override_default_interpreter'], elem)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    show = True
    if not ('display' in config[page.username]['page_security_level'](page.url)
                or interp_kind == None ):
        include_interpreter(interp_kind, page, uid)
        log_id = util.extract_log_id(vlam)
        if log_id:
            t = 'interpreter'
            config[page.username]['logging_uids'][uid] = (log_id, t)
    else:
        log_id = False
        show = False

    # then we can go ahead and add html markup, extracting the Python
    # code to be executed in the process - we will not need this code;
    # this could change in a future version where we could add a button to
    # have the code automatically "injected" and executed by the
    # interpreter, thus saving some typing by the user.

    python_code = util.extract_code(elem)
    if util.is_interpreter_session(python_code):
        elem.attrib['title'] = "pycon"
        python_code = util.extract_code_from_interpreter(python_code)
    else:
        elem.attrib['title'] = "python"
    code, show_vlam = plugin['services'].style(page, elem, None, vlam)
    elem.attrib['title'] = vlam
    if log_id:
        config[page.username]['log'][log_id] = [tostring(elem)]
    util.wrap_in_div(elem, uid, vlam, "interpreter", show_vlam)

    if config[page.username]['popups'] and interp_kind is not None:
        # insert popup helper
        img = Element("img", src="/images/help.png", style="height:32px;",
                title = "cluetip Hello %s! "%page.username + titles[interp_kind],
                rel = help_files[interp_kind])
        elem.append(img)
        plugin['services'].insert_cluetip(page, img, uid)
    plugin['services'].insert_io_subwidget(page, elem, uid,
                        interp_kind=interp_kind, sample_code=python_code, show=show)
    plugin['services'].insert_tooltip(page, elem, uid)
    return

def select_type(vlam, c, elem):
    '''determines the interpreter type that should be inserted based on
       user configuration and vlam information.'''
    if c is None:
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
                return # assume it is not an interpreter session.
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
    return interp_kind

def include_interpreter(interp_kind, page, uid):
    '''includes the relevant code to initialize an interpreter'''
    prefix = config[page.username]['_prefix']
    BorgInterpreter_js = borg_javascript(prefix, page)
    SingleInterpreter_js = single_javascript(prefix, page)
    parrot_js = parrot_javascript(prefix, page)
    Parrots_js = parrots_javascript(prefix, page)
    TypeInfoConsole_js = type_info_javascript(prefix, page)
    # first we need to make sure that the required javacript code is in the page:
    if interp_kind == "borg" or interp_kind == "interpreter":
        if not page.includes("BorgInterpreter_included"):
            page.add_include("BorgInterpreter_included")
            page.add_js_code(BorgInterpreter_js)
        page.add_js_code('init_BorgInterpreter("%s");' % uid)
    elif interp_kind == "isolated" or interp_kind == "Human":
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

def borg_javascript(prefix, page):
    '''create string needed to initialize a Borg interpreter using javascript'''
    return r"""
    function init_BorgInterpreter(uid){
        code = "import src.interpreter\nborg=src.interpreter.BorgConsole(group='%s',username='%s')";
        code += "\nborg.interact()\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """ % (page.pageid, page.username, plugin['session_random_id'])

def single_javascript(prefix, page):
    '''create string needed to initialize an Isolated (single) interpreter
       using javascript'''
    return r"""
    function init_SingleInterpreter(uid){
        code = "import src.interpreter\nisolated=src.interpreter.SingleConsole(username='%s')";
        code += "\nisolated.interact(ps1='--> ')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """ % (page.username, plugin['session_random_id'])

def parrot_javascript(prefix, page):
    '''create string needed to initialize a parrot (single) interpreter
       using javascript'''
    return   r"""
    function init_parrotInterpreter(uid){
        code = "import src.interpreter\nisolated=src.interpreter.SingleConsole(username='%s')";
        code += "\nisolated.interact(ps1='_u__) ', symbol='exec')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """ % (page.username, plugin['session_random_id'])

def parrots_javascript(prefix, page):
    '''create string needed to initialize a parrots (shared) interpreter
       using javascript'''
    return r"""
    function init_ParrotsInterpreter(uid){
        code = "import src.interpreter\nborg=src.interpreter.BorgConsole(group='%s', username='%s')";
        code += "\nborg.interact(ps1='_u__)) ', symbol='exec')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """ % (page.pageid, page.username, plugin['session_random_id'])

def type_info_javascript(prefix, page):
    '''create string needed to initialize a TypeInfo (shared) interpreter
       using javascript'''
    return r"""
    function init_TypeInfoConsole(uid){
        code = "import src.interpreter\nborg=src.interpreter.TypeInfoConsole(group='%s', username='%s')";
        code += "\nborg.interact(ps1='<t>>> ')\n";
        var j = new XMLHttpRequest();
        j.open("POST", "/exec%s?uid="+uid, false);
        j.send(code);
    };
    """ % (page.pageid, page.username, plugin['session_random_id'])

#  Unfortunately, IPython interferes with Crunchy; I'm commenting it out, keeping it in as a reference.

## Note: the code has been edited since the original version has been
## commented out ... and has not been tested.

##IPythonInterpreter_js = r"""
##function init_IPythonInterpreter(uid){
##    code = "import src.interpreter\n";
##    code += "isolated=src.interpreter.SingleConsole()\n";
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
##"""%(sys.version.split(" ")[0], plugin['session_random_id'])
