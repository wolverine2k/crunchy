"""  Crunchy editor plugin.

From some Python code (possibly including a simulated interpreter session)
contained inside a <pre> element, it creates an editor for a user to
enter or modify some code.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API
import CrunchyPlugin

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

# The set of other "widgets/services" provided by this plugin
provides = set(["image_file_widget"])
# The set of other "widgets/services" required from other plugins
requires = set(["io_widget", "/exec", "style_pycode",
               "editor_widget"])

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
    CrunchyPlugin.register_vlam_handler("pre", "image_file", insert_image_file)

def insert_image_file(page, elem, uid, vlam):
    """handles the editor widget"""
    # We add html markup, extracting the Python
    # code to be executed in the process
    code, markup = CrunchyPlugin.services.style_pycode(page, elem)

    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_doctest() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    # determine where the code should appear; we can't have both
    # no-pre and no-copy at the same time
    if not "no-pre" in vlam:
        elem.insert(0, markup)
    elif "no-copy" in vlam:
        code = "\n"
    CrunchyPlugin.services.insert_editor_subwidget(page, elem, uid, code)
    # some spacing:
    et.SubElement(elem, "br")
    # the actual button used for code execution:
    btn = et.SubElement(elem, "button")
    btn.attrib["onclick"] = "image_exec_code('%s')" % uid
    btn.text = "Generate image"
    et.SubElement(elem, "br")
    # an output subwidget:
    CrunchyPlugin.services.insert_io_subwidget(page, elem, uid)
    # Inserting the widget
    try:
        img_fname = vlam.split()[1]
    except IndexError:
        # The user hasn't supplied the filename in the VLAM.
        # I don't know how to respond back to the user.
        raise
    # Extension of the file; used for determining the filetype
    ext = img_fname.rsplit('.',1)[1]
    
    et.SubElement(elem, "br")
    if ext in ['svg', 'svgz']:
        img = et.SubElement(elem, "iframe")
    else:
        img = et.SubElement(elem, "img")
    img.attrib['id'] = 'img_' + uid
    img.attrib['src'] = ''
    img.attrib['alt'] = 'The code above should create a file named ' +\
                        img_fname
    et.SubElement(elem, "br")
    # we need some unique javascript in the page; note how the
    # "/exec" are referred to above as required
    # services appear here
    # with a random session id appended for security reasons.

    image_jscode = """
function image_exec_code(uid){
    img = document.getElementById("img_"+uid);
    img.src = "";

    code=editAreaLoader.getValue("code_"+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%(session_id)s?uid="+uid, false);
    code = '%(pre_code)s' + code + '%(post_code)s';
    j.send(code);

    // This is needed to reload the new image
    j.open("GET", "/working_images/%(img_fname)s", false);
    j.send(null);

    img.src = "/working_images/%(img_fname)s";
    img.alt = "If you see this message, then the code above doesn't work.";
};
"""

    image_jscode = image_jscode%{
    "session_id": CrunchyPlugin.session_random_id,

    "pre_code":\
"""
import os
__current = os.getcwdu()
os.chdir("server_root/working_images")
""".replace('\n', '\\n'),

    "post_code":\
"""
os.chdir(__current)
""".replace('\n', '\\n'),
    "img_fname": img_fname,
}

    # At the end we need to make sure that the required javacript code is
    # in the page.
    if not page.includes("image_included"):
        page.add_include("image_included")
        page.add_js_code(image_jscode)
