"""editarea plugin.  Provides better editing facilities than a
simple textarea.

unit tests in test_editarea.rst
"""
import os
# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, translate, plugin, SubElement
_ = translate['_']

provides = set(["editarea"])
requires = set(["/save_file", "filtered_dir", "insert_file_tree"])

def register():
    '''registers a single service: enable_editarea'''
    plugin['register_service']("enable_editarea", enable_editarea)
    plugin['register_http_handler']("/jquery_file_tree_all", jquery_file_tree_all)

def enable_editarea(page, elem, textarea_id):  # tested
    """enables an editarea editor on a given element (textarea) of a page.
    """
    if not page.includes("editarea_included"):
        page.add_include("editarea_included")
        page.add_js_code(editArea_load_and_save)
        # note: crunchy (handle_default.py) needs all js files loaded to be accessible
        # from the server root; "/.." are not allowed.
        page.insert_js_file("/edit_area/edit_area_crunchy.js")
    # first we need to make sure that the required css code is in the page:
    if not page.includes("hidden_load_and_save"):
        page.add_include("hidden_load_and_save")
        page.add_css_code(load_save_css)
    # element specific code
    page.add_js_code(editAreaLoader_js%(textarea_id,
                                config[page.username]['editarea_language']))
    add_hidden_load_and_save(page, elem, textarea_id)
    return

def add_hidden_load_and_save(page, elem, textarea_id):  # tested
    '''
    adds hidden load and save javascript objects on a page
    '''
    hidden_load_id = 'hidden_load' + textarea_id
    hidden_load = SubElement(elem, 'div', id=hidden_load_id)
    hidden_load.attrib['class'] = 'load_python'
    add_load_python(page, hidden_load, hidden_load_id, textarea_id)

    hidden_save_id = 'hidden_save' + textarea_id
    hidden_save = SubElement(elem, 'div', id=hidden_save_id)
    hidden_save.attrib['class'] = 'save_python'
    add_save_python(page, hidden_save, hidden_save_id, textarea_id)
    return

def insert_file_browser(page, elem, uid, action, title, js_script, klass):
    '''inserts a file tree object in a page.'''
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("jquery_file_tree"):
            page.add_include("jquery_file_tree")
            page.insert_js_file("/javascript/jquery.filetree.js")
            page.insert_css_file("/css/jquery.filetree.css")
    else:
        return
    tree_id = "tree_" + uid
    root = os.path.splitdrive(__file__)[0] + "/"  # use base directory for now
    js_code =  """$(document).ready( function() {
        $('#%s').fileTree({
          root: '%s',
          script: '%s',
          expandSpeed: -1,
          collapseSpeed: -1,
          multiFolder: false
        }, function(file) {
            %s
        });
    });
    """ % (tree_id, root, action, js_script)
    page.add_js_code(js_code)
    elem.text = title
    elem.attrib['class'] = klass

    file_div = SubElement(elem, 'div')
    file_div.attrib['id'] = tree_id
    file_div.attrib['class'] = "filetree_window"
    return

def add_load_python(page, parent, hidden_load_id, textarea_id):
    '''Inserts the widget required to browse for and load a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    js_script = """path = file;
                   load_python_file('%s')""" % textarea_id
    insert_file_browser(page, parent, hidden_load_id, '/jquery_file_tree_all',
                 _('Select a file to open'), js_script, "load_python")
    btn = SubElement(parent, 'button',
        onclick="c=getElementById('%s');c.style.visibility='hidden';c.style.zIndex=-1;"%hidden_load_id)
    btn.text = _("Cancel")
    return


def filter_none(filename, dummy):
    '''filters out all files and directory with filename so as to exclude
       files whose names start with "." with the possible
       exception of ".crunchy" - the usual crunchy default directory.
    '''
    if filename.startswith('.') and filename != ".crunchy":
        return True
    else:
        return False

def jquery_file_tree_all(request):
    '''extract the file information and formats it in the form expected
       by the jquery FileTree plugin, but excludes some normally hidden
       files or directories, to include only python files.'''
    plugin['services'].filtered_dir(request, filter_none)
    return

def add_save_python(page, parent, hidden_save_id, textarea_id):
    '''Inserts the widget required to browse for and save a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    input_id = "input_" + hidden_save_id
    js_saved_script = """save_python_file(document.getElementById('%s').value,
                        '%s');""" % (input_id, textarea_id)
    SubElement(parent, "br")
    SubElement(parent, 'input', name='url', size='60', id=input_id)
    SubElement(parent, "br")
    btn = SubElement(parent, 'button', onclick=js_saved_script)
    btn.text = _("Save file")

    js_script = """document.getElementById('%s').value=file;""" % input_id
    insert_file_browser(page, parent, hidden_save_id, '/jquery_file_tree_all',
                 _('Select a file to save'), js_script, "save_python")
    btn = SubElement(parent, 'button',
        onclick="c=getElementById('%s');c.style.visibility='hidden';c.style.zIndex=-1;"%hidden_save_id)
    btn.text = _("Cancel")
    return

editArea_load_and_save = """
function my_load_file(id){
var obj = document.getElementById('hidden_load'+id);
obj.style.zIndex = 99999;
obj.style.visibility = "visible";
}
function my_save_file(id){
var obj = document.getElementById('hidden_save'+id);
obj.style.zIndex = 99999;
obj.style.visibility = "visible";
}

function load_python_file(obj_id)
{
    e = document.getElementById(obj_id);
    e.innerHTML = '';
    var h = new XMLHttpRequest()
    h.onreadystatechange = function()
        {
            if (h.readyState == 4)
            {
                try
                {
                    var status = h.status;
                }
                catch(e)
                {
                    var status = "NO HTTP RESPONSE";
                }
                switch (status)
                {
                case 200:
                    //alert(h.responseText);
                    editAreaLoader.setValue(obj_id, h.responseText);
                    var obj = document.getElementById('hidden_load'+obj_id);
                    obj.style.visibility = "hidden";
                    obj.style.zIndex = -1;
                    break;
                case 12029:
                    //IE could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + ": " + h.responseText);
                }
            }
        };
    h.open("GET", "/load_file"+"?"+"path="+path, true);
    try{
        document.getElementById("path_"+obj_id.substring(5)).innerHTML = path;
        }
    catch (e){};
    h.send('');
}
function save_python_file(path, id)
{
    if (path == ''){
        alert("No file specified");
        var obj = document.getElementById('hidden_save'+id);
        obj.style.visibility = "hidden";
        obj.style.zIndex = -1;
        return;
    }
    else{
        obj = document.getElementById('run_from_file_'+id.substring(5));
        obj.style.visibility = "visible";
        obj.style.display = "inline";
    }
    data = document.getElementById(id).value;
    try{
        document.getElementById("path_"+id.substring(5)).innerHTML = path;
        }
    catch (e){};
    var j = new XMLHttpRequest();
	j.open("POST", "/save_file", true);
	// Use an unlikely part of a filename (path) as a separator between file
	// path and file content.
	j.send(path+"_::EOF::_"+editAreaLoader.getValue(id));
    var obj = document.getElementById('hidden_save'+id);
    obj.style.visibility = "hidden";
    obj.style.zIndex = -1;
};
"""

# Some javascript code
editAreaLoader_js = """
editAreaLoader.init({
id: "%s",
font_size: "11",
allow_resize: "both",
allow_toggle: true,
language: "%s",
toolbar: "new_document, save, load, |, fullscreen, |, search, go_to_line, |, undo, redo, |, select_font, |, syntax_selection, |, change_smooth_selection, highlight, reset_highlight, |, help",
syntax: "python",
syntax_selection_allow: "python,html,css,js,php,vb,xml,c,cpp,sql,basic,pas,brainfuck,perl,ruby,coldfusion,robotstxt,tsql",
start_highlight: true,
load_callback:"my_load_file",
save_callback:"my_save_file",
display: "later",
replace_tab_by_spaces:4,
min_height: 150});"""

# css stuff
load_save_css = """
   /* Load and save python forms. These are in a fixed position
    the screen so that they can be seen even when the editor is
    in fullscreen mode.  z-index of editarea when toggled is 9999 */

.load_python{position: fixed; top: 100px; z-index:-1;
            border: 4px solid #339; border-style: outset;
            visibility: hidden; background-color: #66C;
            color: white; font: 16pt; padding: 15px;}
.save_python{position: fixed; top: 200px; z-index:-1;
            border: 4px solid #063; border-style: outset;
            visibility: hidden; background-color:#696;
            color: white; font: 16pt; padding: 15px;}
"""
