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
from src.utilities import extract_log_id
import src.session as session
_ = translate['_']

# The set of other "widgets/services" provided by this plugin
provides = set(["editor_widget"])
# The set of other "widgets/services" required from other plugins
requires = set(["io_widget", "/exec", "/run_external", "style_pycode",
               "editarea"])

def register():
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
    plugin['register_service']("insert_editor_subwidget", insert_editor_subwidget)
    plugin['register_tag_handler']("pre", "title", "alternate_python_version",
                                                        insert_alternate_python)
    # shorter name version of the above
    plugin['register_tag_handler']("pre", "title", "alt_py",
                                                        insert_alternate_python)
    # the following should never be used other than by Crunchy developers
    # for testing purposes
    plugin['register_tag_handler']("pre", "title", "_test_sanitize_for_ElementTree",
                                                        _test_sanitize_for_ElementTree)

def insert_editor_subwidget(page, elem, uid, code="\n"):
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

def insert_editor(page, elem, uid):
    """handles the editor widget"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'editor'
        session.add_log_id(uid, log_id, t)
        #config['logging_uids'][uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config['page_security_level'](page.url):
        if not page.includes("exec_included"):
            page.add_include("exec_included")
            page.add_js_code(exec_jscode)
    # then we can go ahead and add html markup, extracting the Python
    # code to be executed in the process
    code, markup, dummy = plugin['services'].style_pycode(page, elem)
    if log_id:
        session.log(uid, tostring(markup))
        #config['log'][log_id] = [tostring(markup)]
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_pycode() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.

    insert_markup(elem, uid, vlam, markup)

    if (("no-copy" in vlam) and not ("no-pre" in vlam)) or (not code):
        code = "\n"
    plugin['services'].insert_editor_subwidget(page, elem, uid, code)
    #some spacing if buttons are needed, they appear below.
    if "external in vlam" or not "no-internal" in vlam:
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
    path_label.text = config['temp_dir'] + os.path.sep + "temp.py"

    if "external" in vlam:
        btn.attrib["onclick"] = "exec_code_externally('%s')" % uid
        btn.text = _("Execute as external program")
        if log_id:  # override - probably not useful to log
            t = 'run_external_editor'
            session.add_log_id(uid, log_id, t)
            #config['logging_uids'][uid] = (log_id, t)
        path_label.attrib['class'] = 'path_info'
        if not "no-internal" in vlam:
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
    """handles the python widget"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'editor'
        session.add_log_id(uid, log_id, t)
        #config['logging_uids'][uid] = (log_id, t)

    if 'display' not in config['page_security_level'](page.url):
        if not page.includes("exec_included"):
            page.add_include("exec_included")
            page.add_js_code(exec_jscode)

    code, markup, dummy = plugin['services'].style_pycode(page, elem)
    if log_id:
        session.log(uid, tostring(markup))
        #config['log'][log_id] = [tostring(markup)]

    insert_markup(elem, uid, vlam, markup)

    if (("no-copy" in vlam) and not ("no-pre" in vlam)) or (not code):
        code = "\n"
    plugin['services'].insert_editor_subwidget(page, elem, uid, code)

    form1 = SubElement(elem, 'form', name='form1_')
    span = SubElement(form1, 'span')
    span.text = _('Alternate Python path: ')
    span.attrib['class'] = 'alt_python'
    input1 = SubElement(form1, 'input', id='input1_'+uid, size='50',
                            value=config['alternate_python_version'])
    input1.attrib['class'] = 'alt_python'
    SubElement(elem, "br")

    btn = SubElement(elem, "button")
    path_label = SubElement(elem, "span")
    path_label.attrib['id'] = 'path_' + uid
    path_label.text = config['temp_dir'] + os.path.sep + "temp.py"

    btn.attrib["onclick"] = "exec_code_externally_python_interpreter('%s')" % uid
    btn.text = _("Execute as external program")
    path_label.attrib['class'] = 'path_info'

def _test_sanitize_for_ElementTree(page, elem, uid):
    """the purpose of this function is ONLY to provide a separate way of
       launching sanitize.py as a means of testing it.

       From the (initial) description of sanitize.py:
       The purpose of sanitize.py is to process an html file (that could be
       malformed) using a combination of BeautifulSoup and ElementTree and
       output a "cleaned up" file based on a given security level.

       This script is meant to be run as a standalone module, using Python 2.x.
       It is expected to be launched via exec_external_python_version() located
       in file_service.py.

       The input file name is expected to be in.html, located in Crunchy's temp
       directory.  The output file name is out.html, also located in Crunchy's
       temp directory.
       """
    vlam = elem.attrib["title"]
    if 'display' not in config['page_security_level'](page.url):
        if not page.includes("exec_included"):
            page.add_include("exec_included")
            page.add_js_code(exec_jscode)
    filepath = os.path.join(plugin['get_root_dir'](), 'sanitize.py')
    f = open(filepath)
    elem.text = f.read()
    code, markup, dummy = plugin['services'].style_pycode(page, elem)

    insert_markup(elem, uid, vlam, markup)

    plugin['services'].insert_editor_subwidget(page, elem, uid, code)

    btn = SubElement(elem, "button")
    path_label = SubElement(elem, "span")
    path_label.attrib['id'] = 'path_' + uid
    filepath2 = os.path.join(plugin['get_root_dir'](), 'sanitize_new.py')
    path_label.text = filepath2

    btn.attrib["onclick"] = "exec_code_externally('%s')" % uid
    btn.text = _("Execute as external program")
    path_label.attrib['class'] = 'path_info'

def insert_markup(elem, uid, vlam, markup):
    '''clears an element and inserts the new markup inside it'''
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = "crunchy"
    if not "no-pre" in vlam:
        try:
            elem.insert(0, markup)
        except AssertionError:  # this should never happen
            elem.insert(0, Element("br"))
            bold = Element("b")
            span = Element("span")
            span.text = "AssertionError from ElementTree"
            bold.append(span)
            elem.insert(1, bold)

# we need some unique javascript in the page; note how the
# "/exec"  and /run_external handlers referred to above as required
# services appear here
# with a random session id appended for security reasons.
exec_jscode = """
function exec_code(uid){
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
