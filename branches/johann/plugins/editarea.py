"""editarea plugin.  Provides better editing facilities than a
simple textarea.
"""

provides = set(["editarea"])

import CrunchyPlugin

# for now, this is just a default
language = "en"

def register():
    CrunchyPlugin.register_service(enable_editarea, "enable_editarea")

def enable_editarea(page, uid):
    """enables an editarea editor on a given element (textarea) of a page.
    """
    if not page.includes("editarea_included"):
        page.add_include("editarea_included")
        page.add_js_code(editArea_load_and_save)
        # note: crunchy (handle_default.py) needs all js files loaded to be accessible
        # from the server root; ".." are not allowed.
        page.insert_js_file("/edit_area/edit_area_crunchy.js")
    # element specific code
    page.add_js_code(editAreaLoader_js%('"code_'+uid+'"', language))
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
"""

# Some javascript code
editAreaLoader_js = """
editAreaLoader.init({
id: %s,
browsers: "all",
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
