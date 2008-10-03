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
    dummy, show_vlam = plugin['services'].style(page, elem, None, vlam)
    elem.attrib['title'] = vlam
    if log_id:
        config[page.username]['log'][log_id] = [tostring(elem)]
    util.wrap_in_div(elem, uid, vlam, "editor", show_vlam)
    if config[page.username]['popups']:
        # insert popup helper
        img = Element("img", src="/images/help.png",
                title = "cluetip Hello %s! "%page.username + "This is an Editor.",
                rel = "/docs/popups/editor.html")
        elem.append(img)
        plugin['services'].insert_cluetip(page, img, uid)

    if (("no_copy" in vlam) and not ("no_pre" in vlam)) or (not python_code):
        python_code = "\n"
    plugin['services'].insert_editor_subwidget(page, elem, uid, python_code)
    return vlam

def insert_editor(page, elem, uid):
    """handles the editor widget"""

    vlam = insert_bare_editor(page, elem, uid)
    #log_id = util.extract_log_id(vlam)
    SubElement(elem, "br")
    if not "no_internal" in vlam:
        btn1 = SubElement(elem, "button")
        btn1.attrib["onclick"] = "exec_code('%s')" % uid
        SubElement(elem, "br")
    btn2 = SubElement(elem, "button", id="run_from_file_"+uid)
    btn2.attrib["onclick"] = "exec_code_externally('%s')" % uid
    btn2.text = _("Run from file")
    path_label = SubElement(elem, "span")
    path_label.attrib['id'] = 'path_' + uid
    path_label.attrib['class'] = 'path_info'

    if "external" in vlam:
        path_label.text = config[page.username]['temp_dir'] + os.path.sep + "temp.py"
        if "analyzer_score" in vlam:
            plugin['services'].add_scoring(page, btn2, uid)
        if not "no_internal" in vlam:
            btn1.text = _("Execute as separate thread")
    else:
        path_label.text = "" # effectively hides it.
        btn1.text = _("Execute")
        # Note that btn2 will be revealed by execution code when a file is saved;
        # see editarea.py for this.
        btn2.attrib['style'] = "display:none;"
        if "analyzer_score" in vlam:
            plugin['services'].add_scoring(page, btn1, uid)

    if "analyzer_report" in vlam:
        SubElement(elem, "br")
        plugin['services'].insert_analyzer_button(page, elem, uid)
    SubElement(elem, "br")
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
    if "analyzer_score" in vlam:
        plugin['services'].add_scoring(page, btn, uid)
    if "analyzer_report" in vlam:
        plugin['services'].insert_analyzer_button(page, elem, uid)

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
