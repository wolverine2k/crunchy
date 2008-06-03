"""editarea plugin.  Provides better editing facilities than a
simple textarea.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, translate, plugin, SubElement
_ = translate['_']

provides = set(["editarea"])
requires = set(["/save_file", "/load_file"])

def register():
    '''registers a single service: enable_editarea'''
    plugin['register_service']("enable_editarea", enable_editarea)

def enable_editarea(page, elem, textarea_id):
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
                                config['editarea_language']))
    add_hidden_load_and_save(elem, textarea_id)
    return

def add_hidden_load_and_save(elem, textarea_id):
    '''
    adds hidden load and save javascript objects on a page
    '''
    hidden_load_id = 'hidden_load' + textarea_id
    hidden_load = SubElement(elem, 'div', id=hidden_load_id)
    hidden_load.attrib['class'] = 'load_python'
    addLoadPython(hidden_load, hidden_load_id, textarea_id)

    hidden_save_id = 'hidden_save' + textarea_id
    hidden_save = SubElement(elem, 'div', id=hidden_save_id)
    hidden_save.attrib['class'] = 'save_python'
    addSavePython(hidden_save, hidden_save_id, textarea_id)
    return

def addLoadPython(parent, hidden_load_id, textarea_id):
    '''Inserts the two forms required to browse for and load a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    filename = 'filename' + hidden_load_id
    path = 'path' + hidden_load_id
    SubElement(parent, 'br')
    form1 = SubElement(parent, 'form',
                onblur = "$('#%s').val($('#%s').val());"%(path, filename)) # path.val = filename.val
    SubElement(form1, 'input', type='file', id=filename, size='80')
    SubElement(form1, 'br')
    
    form2 = SubElement(parent, 'form')
    SubElement(form2, 'input', type='hidden', id=path)
    btn = SubElement(parent, 'button',
        onclick="load_python_file($('#&s').val(), '%s');" % (path, textarea_id))
    btn.text = _("Load Python file")
    btn2 = SubElement(parent, 'button',
        onclick="$('#%s').hide();"%hidden_load_id)
    btn2.text = _("Cancel");
    return

def addSavePython(parent, hidden_save_id, textarea_id):
    '''Inserts the two forms required to browse for and load a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    filename = 'filename' + hidden_save_id
    path = 'path' + hidden_save_id
    SubElement(parent, 'br')
    form1 = SubElement(parent, 'form')
    SubElement(form1, 'input', type='file', id=filename, size='80')
    SubElement(form1, 'br')

    form2 = SubElement(parent, 'form')
    form2.text = _("Use 'Save and Run' to execute programs (like pygame and GUI based ones) externally.")
    SubElement(form2, 'input', type='hidden', id=path)
    btn = SubElement(parent, 'button',
        onclick="$('#%s').val($('#%s').val());"%(path, filename)+
        "save_python_file($('#%s').val(), '%s');"%(path, textarea_id))
    btn.text = _("Save Python file")
    btn2 = SubElement(parent, 'button',
        onclick="$('#%s').hide();"%hidden_save_id)
    btn2.text = _("Cancel")
    btn3 = SubElement(parent, 'button',
        onclick="$('#%s').val($('#%s').val());"%(path, filename)+
        "save_and_run($('#%s').val(), '%s');"%(path, textarea_id))
    btn3.text = _("Save and Run")
    return

editArea_load_and_save = """
function my_load_file(id){
    $("#hidden_load"+id).show();
};

function my_save_file(id){
    $("#hidden_save"+id).show();
}

function load_python_file(path, obj_id)
{
    $("#"+obj_id).html("");
    $("#path_"+id.substring(5)).html(path);
    $.get("/load_file", {path : path}, function(data, status){
        editAreaLoader.setValue(obj_id, data);
        $('#hidden_save'+id).hide();
    });
};

function save_python_file(path, id)
{
    var data = $("#"+id).val();
    $("#path_"+id.substring(5)).html(path);
    $.ajax({type : "POST",
            url : "/save_file",
            // Use an unlikely part of a filename (path) as a separator between file
        	// path and file content.
            data : path+"_::EOF::_"+editAreaLoader.getValue(id),
            processData : false
            });
    $('#hidden_save'+id).hide();
};

function save_and_run(path, id)
{
    data = $("#"+id).val();
    $("#path_"+id.substring(5)).html(path);
    $.ajax({type : "POST",
            url : "/save_and_run%s",
            // Use an unlikely part of a filename (path) as a separator between file
        	// path and file content.
            data : path+"_::EOF::_"+editAreaLoader.getValue(id),
            processData : false
            });
    var obj =$('#hidden_save'+id).hide();
};""" % plugin['session_random_id']

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

.load_python{position:fixed; top:100px; z-index:-1;
            border:4px solid #339; border-style: outset;
            visibility:hidden; background-color:#66C}
.save_python{position:fixed; top:200px; z-index:-1;
            border:4px solid #063; border-style: outset;
            visibility:hidden; background-color:#696}
"""
