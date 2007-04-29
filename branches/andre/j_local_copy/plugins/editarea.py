"""editarea plugin.  Provides better editing facilities than a
simple textarea.
"""

import CrunchyPlugin

# Third party modules - included in crunchy distribution
from element_tree import ElementTree as et

# for now, this is just a default
language = "en"

# placeholder for future translation service...
def _(data):
    return data

provides = set(["editarea"])
requires = set(["/save_file", "/load_file"])

def register():
    CrunchyPlugin.register_service(enable_editarea, "enable_editarea")

def enable_editarea(page, elem, uid, textarea_id):
    """enables an editarea editor on a given element (textarea) of a page.
    """
    if not page.includes("editarea_included"):
        page.add_include("editarea_included")
        page.add_js_code(editArea_load_and_save)
        # note: crunchy (handle_default.py) needs all js files loaded to be accessible
        # from the server root; ".." are not allowed.
        page.insert_js_file("/edit_area/edit_area_crunchy.js")
    # first we need to make sure that the required css code is in the page:
    if not page.includes("hidden_load_and_save"):
        page.add_include("hidden_load_and_save")
        page.add_css_code(load_save_css)
    # element specific code
    page.add_js_code(editAreaLoader_js%(textarea_id, language))
    add_hidden_load_and_save(elem, uid, textarea_id)
    return

def add_hidden_load_and_save(elem, id, textarea_id):
    hidden_load_id = 'hidden_load' + textarea_id
    hidden_load = et.SubElement(elem, 'div', id=hidden_load_id)
    hidden_load.attrib['class'] = 'load_python'
    addLoadPython(hidden_load, hidden_load_id, textarea_id)

    hidden_save_id = 'hidden_save' + textarea_id
    hidden_save = et.SubElement(elem, 'div', id=hidden_save_id)
    hidden_save.attrib['class'] = 'save_python'
    addSavePython(hidden_save, hidden_save_id, textarea_id)
    return

def addLoadPython(parent, hidden_load_id, textarea_id):
    '''Inserts the two forms required to browse for and load a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    filename = 'filename' + hidden_load_id
    path = 'path' + hidden_load_id
    br = et.SubElement(parent, 'br')
    form1 = et.SubElement(parent, 'form',
                onblur = "a=getElementById('%s');b=getElementById('%s');a.value=b.value"%(path, filename))
    input1 = et.SubElement(form1, 'input', type='file', id=filename, size='80')
    br = et.SubElement(form1, 'br')

    form2 = et.SubElement(parent, 'form')
    input2 = et.SubElement(form2, 'input', type='hidden', id=path)
    btn = et.SubElement(parent, 'button',
        onclick="c=getElementById('%s');path=c.value;load_python_file('%s');"%(path, textarea_id))
    btn.text = _("Load Python file")
    btn2 = et.SubElement(parent, 'button',
        onclick="c=getElementById('%s');path=c.style.visibility='hidden';"%hidden_load_id)
    btn2.text = _("Cancel")
    return

def addSavePython(parent, hidden_save_id, textarea_id):
    '''Inserts the two forms required to browse for and load a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    filename = 'filename' + hidden_save_id
    path = 'path' + hidden_save_id
    br = et.SubElement(parent, 'br')
    form1 = et.SubElement(parent, 'form')
    input1 = et.SubElement(form1, 'input', type='file', id=filename, size='80')
    br = et.SubElement(form1, 'br')

    form2 = et.SubElement(parent, 'form')
    form2.text = _("Use 'Save and Run' to execute programs (like pygame and GUI based ones) externally.")
    input2 = et.SubElement(form2, 'input', type='hidden', id=path)
    btn = et.SubElement(parent, 'button',
        onclick="a=getElementById('%s');b=getElementById('%s');a.value=b.value;"%(path, filename)+
        "c=getElementById('%s');path=c.value;save_python_file(path,'%s');"%(path, textarea_id))
    btn.text = _("Save Python file")
    btn2 = et.SubElement(parent, 'button',
        onclick="c=getElementById('%s');path=c.style.visibility='hidden';"%hidden_save_id)
    btn2.text = _("Cancel")
    btn3 = et.SubElement(parent, 'button',
        onclick="a=getElementById('%s');b=getElementById('%s');a.value=b.value;"%(path, filename)+
        "c=getElementById('%s');path=c.value;save_and_run(path,'%s');"%(path, textarea_id))
    btn3.text = _("Save and Run")
    return


editArea_load_and_save = """
function my_load_file(id){
var obj = document.getElementById('hidden_load'+id);
obj.style.visibility = "visible";
}
function my_save_file(id){
var obj = document.getElementById('hidden_save'+id);
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
    h.send('');
}
function save_python_file(path, id)
{
	data = document.getElementById(id).value;
    var j = new XMLHttpRequest();
	j.open("POST", "/save_file", true);
	// Use an unlikely part of a filename (path) as a separator between file
	// path and file content.
	j.send(path+"_::EOF::_"+editAreaLoader.getValue(id));
    var obj = document.getElementById('hidden_save'+id);
    obj.style.visibility = "hidden";
};

function save_and_run(path, id)
{
	data = document.getElementById(id).value;
	h = get_http();
	h.open("POST", "/save_and_run"+session_id, true);
	// Use an unlikely part of a filename (path) as a separator between file
	// path and file content.
	h.send(path+"_::EOF::_"+editAreaLoader.getValue(id));
  var obj = document.getElementById('hidden_save'+id);
	obj.style.visibility = "hidden";
};"""

# Some javascript code
editAreaLoader_js = """
editAreaLoader.init({
id: "%s",
font_size: "11",
allow_resize: "both",
allow_toggle: true,
language: "%s",
toolbar: "new_document, save, load, |, fullscreen, |, search, go_to_line, |, undo, redo, |, select_font, |, change_smooth_selection, highlight, reset_highlight, |, help",
syntax: "python",
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

.load_python{position:fixed; top:100px; z-index:99999;
            border:4px solid #339; border-style: outset;
            visibility:hidden; background-color:#66C}
.save_python{position:fixed; top:200px; z-index:99999;
            border:4px solid #063; border-style: outset;
            visibility:hidden; background-color:#696}
"""
