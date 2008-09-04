"""  Crunchy editor plugin.

From some Python code (possibly including a simulated interpreter session)
contained inside a <pre> element, it creates an editor for a user to
enter or modify some code.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

import os

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, Element, SubElement, translate, tostring
import src.utilities as util
_ = translate['_']

# The set of other "widgets/services" provided by this plugin
provides = set(["editor_widget"])
# The set of other "widgets/services" required from other plugins
requires = set(["io_widget", "/exec", "/run_external", "style_pycode",
               "editarea"])

def register():  # tested
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom service to insert an editor when requested by this or
          another plugin.
       """
    # 'editor' only appears inside <pre> elements, using the notation
    # <pre title='editor ...'>
    plugin['register_tag_handler']("pre", "title", "editor",
                                                        insert_editor)
    plugin['register_tag_handler']("pre", "title", "alternate_python_version",
                                                        insert_alternate_python)
    # shorter name version of the above
    plugin['register_tag_handler']("pre", "title", "alt_py",
                                                        insert_alternate_python)
    plugin['add_vlam_option']('no_markup', 'editor', 'alternate_python_version',
                              'alt_py')
    plugin['register_service']("insert_editor_subwidget", insert_editor_subwidget)
    return

def insert_editor_subwidget(page, elem, uid, code="\n"):  # tested
    """inserts an Elementtree that is an editor,
    used to provide a basic insert_editor_subwidget service
    """
    inp = SubElement(elem, "textarea")
    inp.attrib["rows"] = "10"
    inp.attrib["cols"] = "80"
    editor_id = "code_" + uid
    inp.attrib["id"] = editor_id
    if code == "":
        code = "\n"
    inp.text = code
    plugin['services'].enable_editarea(page, elem, editor_id)

def insert_bare_editor(page, elem, uid):
    """inserts a 'bare' editor, python code, but no execution buttons.

    Common code to both insert_editor() and insert_alternate_python().
    """
    vlam = elem.attrib["title"]
    log_id = util.extract_log_id(vlam)
    if log_id:
        t = 'editor'
        config[page.username]['logging_uids'][uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either,
    # thus making the source easier to read.
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("exec_included"):
            page.add_include("exec_included")
            page.add_js_code(exec_jscode)
    # then we can go ahead and add html markup, extracting the Python
    # code to be executed in the process
    python_code = util.extract_code(elem)
    if util.is_interpreter_session(python_code):
        elem.attrib['title'] = "pycon"
        python_code = util.extract_code_from_interpreter(python_code)
    else:
        elem.attrib['title'] = "python"
    code = plugin['services'].style(page, elem)
    elem.attrib['title'] = "vlam"
    if log_id:
        config[page.username]['log'][log_id] = [tostring(elem)]
    util.wrap_in_div(elem, uid, vlam, "editor")
    if config[page.username]['popups']:
        # insert popup helper
        img = Element("img", src="/images/help.png",
                title = "cluetip Hello %s! "%page.username + "This is a Editor.",
                rel = "/docs/popups/editor.html")
        elem.append(img)
        plugin['services'].insert_cluetip(page, img, uid)

    if (("no_copy" in vlam) and not ("no_pre" in vlam)) or (not python_code):
        python_code = "\n"
    plugin['services'].insert_editor_subwidget(page, elem, uid, python_code)
    return vlam

def insert_editor(page, elem, uid):  # tested
    """handles the editor widget"""

    vlam = insert_bare_editor(page, elem, uid)
    log_id = util.extract_log_id(vlam)
     #some spacing if buttons are needed, they appear below.
    if "external in vlam" or not "no_internal" in vlam:
        SubElement(elem, "br")
    # the actual buttons used for code execution; we make sure the
    # button for external execution, if required, appear first.
    #
    # note: as the code is written, it is possible that an execution
    # button will NOT be included.  Perhaps the tutorial writer wants
    # the user to only execute code from the "save and run" option
    # of the editor...

    btn = SubElement(elem, "button")
    # path_label required in all cases to avoid javascript error
    path_label = SubElement(elem, "span")
    path_label.attrib['id'] = 'path_' + uid
    path_label.text = config[page.username]['temp_dir'] + os.path.sep + "temp.py"

    if "external" in vlam:
        btn.attrib["onclick"] = "exec_code_externally('%s')" % uid
        btn.text = _("Execute as external program")
        if log_id:  # override - probably not useful to log
            t = 'run_external_editor'
            config[page.username]['logging_uids'][uid] = (log_id, t)
        path_label.attrib['class'] = 'path_info'
        if not "no_internal" in vlam:
            SubElement(elem, "br")
            btn2 = SubElement(elem, "button")
            btn2.attrib["onclick"] = "exec_code('%s')" % uid
            btn2.text = _("Execute as separate thread")
    else:
        path_label.attrib['style'] = 'display:none'  #keep hidden since not required
        btn.attrib["onclick"] = "exec_code('%s')" % uid
        btn.text = _("Execute")

    # leaving some space to start output on next line, below last button
    SubElement(elem, "br")
    # an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

def insert_alternate_python(page, elem, uid):
    """inserts the required widget to launch a Python script using
    an alternate Python version.
    """

    vlam = insert_bare_editor(page, elem, uid)

    form1 = SubElement(elem, 'form', name='form1_')
    span = SubElement(form1, 'span')
    span.text = _('Alternate Python path: ')
    span.attrib['class'] = 'alt_python'
    input1 = SubElement(form1, 'input', id='input1_'+uid, size='50',
                            value=config[page.username]['alternate_python_version'])
    input1.attrib['class'] = 'alt_python'
    SubElement(elem, "br")

    btn = SubElement(elem, "button")
    btn.attrib["onclick"] = "exec_code_externally_python_interpreter('%s')" % uid
    btn.text = _("Execute as external program")

    path_label = SubElement(elem, "span", id= 'path_'+uid)
    path_label.text = config[page.username]['temp_dir'] + os.path.sep + "temp.py"
    path_label.attrib['class'] = 'path_info'

# we need some unique javascript in the page; note how the
# "/exec"  and /run_external handlers referred to above as required
# services appear here
# with a random session id appended for security reasons.
exec_jscode = """
function exec_code(uid){
    try{
    document.getElementById("kill_image_"+uid).style.display = "inline";
    document.getElementById("kill_"+uid).style.display="inline";
    }
    catch(err){;} /* may not exist if ctypes not present. */
    code=editAreaLoader.getValue("code_"+uid);
    if (code == undefined) {
        code = document.getElementById("code_"+uid).value;
    }
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%s?uid="+uid, false);
    j.send(code);
};
function exec_code_externally(uid){
    code=editAreaLoader.getValue("code_"+uid);
    if (code == undefined) {
        code = document.getElementById("code_"+uid).value;
    }
    path = document.getElementById("path_"+uid).innerHTML;
    var j = new XMLHttpRequest();
    j.open("POST", "/save_and_run%s?uid="+uid, false);
    j.send(path+"_::EOF::_"+code);
};
function exec_code_externally_python_interpreter(uid){
    code=editAreaLoader.getValue("code_"+uid);
    if (code == undefined) {
        code = document.getElementById("code_"+uid).value;
    }
    path = document.getElementById("path_"+uid).innerHTML;
    var j = new XMLHttpRequest();
    j.open("POST", "/save_and_run_python_interpreter%s?uid="+uid, false);
    inp = document.getElementById("input1_"+uid).value;
    j.send(inp+"_::EOF::_"+path+"_::EOF::_"+code);
};

""" % (plugin['session_random_id'], plugin['session_random_id'],
       plugin['session_random_id'])
