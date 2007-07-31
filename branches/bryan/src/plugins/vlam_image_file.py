"""  Crunchy image file plugin.

plugin used to display an image generated by some Python code.

This file is heavily commented in case someone needs some detailed
example as to how to write a plugin.
"""

import os

# All plugins should import the crunchy plugin API
import src.CrunchyPlugin as CrunchyPlugin
from src.configuration import defaults

# The set of "widgets/services" provided by this plugin
provides = set(["image_file_widget"])
# The set of other "widgets/services" required from other plugins
requires = set(["io_widget", "/exec", "style_pycode",  "editor_widget"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register only one type of action:
          a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       """
    # 'image_file' only appears inside <pre> elements, using the notation
    # <pre title='image_file ...'>
    CrunchyPlugin.register_tag_handler("pre", "title", "image_file",
                                            insert_image_file)

def insert_image_file(page, elem, uid):
    """handles the insert image file widget"""
    vlam = elem.attrib["title"]
    # We add html markup, extracting the Python
    # code to be executed in the process
    code, markup = CrunchyPlugin.services.style_pycode(page, elem)

    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_pycode() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_" + uid
    # extracting the image file name
    stripped_vlam = vlam.strip()
    args = stripped_vlam.split()
    if len(args) >1:
        img_fname = args[1]  # assume name is first argument
    else:
        # The user hasn't supplied the filename in the VLAM.
        elem.insert(0, markup)
        message = CrunchyPlugin.SubElement(elem, "p")
        message.text = """
        The above code was supposed to be used to generate an image.
        However, Crunchy could not find a file name to save the image, so
        only code styling has been performed.
        """
        return

    # determine where the code should appear; we can't have both
    # no-pre and no-copy at the same time; both are optional.
    if not "no-pre" in vlam:
        elem.insert(0, markup)
    elif "no-copy" in vlam:
        code = "\n"
    CrunchyPlugin.services.insert_editor_subwidget(page, elem, uid, code)
    # some spacing:
    CrunchyPlugin.SubElement(elem, "br")

    # the actual button used for code execution:
    btn = CrunchyPlugin.SubElement(elem, "button")
    btn.attrib["onclick"] = "image_exec_code('%s', '%s')" % (uid, img_fname)
    btn.text = "Generate image"  # This will eventually need to be translated

    btn2 = CrunchyPlugin.SubElement(elem, "button")
    btn2.attrib["onclick"] = "load_image('%s', '%s')"%(uid, img_fname)
    btn2.text = "Load image"

    CrunchyPlugin.SubElement(elem, "br")
    # an output subwidget:
    CrunchyPlugin.services.insert_io_subwidget(page, elem, uid)

    # Extension of the file; used for determining the filetype
    ext = img_fname.split('.')[-1]
    CrunchyPlugin.SubElement(elem, "br")
    # KEEP .... as a reminder
##    if ext in ['svg', 'svgz']:  # currently untested
##        img = CrunchyPlugin.SubElement(elem, "iframe")
##    else:
##        img = CrunchyPlugin.SubElement(elem, "img")
    img = CrunchyPlugin.SubElement(elem, "img")
    img.attrib['id'] = 'img_' + uid
    img.attrib['src'] = '/generated_image?url=%s'%img_fname
    img.attrib['alt'] = 'The code above should create a file named ' +\
                        img_fname + '.'
    CrunchyPlugin.SubElement(elem, "br")

    # we need some unique javascript in the page; note how the
    # "/exec" referred to above as a required service appears here
    # with a random session id appended for security reasons.
    #


    image_jscode = """
function image_exec_code(uid, image_name){
    // execute the code
    code=editAreaLoader.getValue('code_'+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%(session_id)s?uid="+uid, false);
    code = '%(pre_code)s' + code + '%(post_code)s';
    j.send(code)
    // now load newly created image
    img = document.getElementById('img_'+uid);
    // fool the browser into thinking this is a new name so it does not cache
    var now = new Date();
    img.src = "/generated_image"+now.getTime()+"?url="+image_name;
    img.alt = 'Image file saved as ' + image_name + '.';
    img.alt = img.alt + '%(error_message)s';
};
"""%{
    "session_id": CrunchyPlugin.session_random_id,
        "pre_code": """
import os
__current = os.getcwdu()
os.chdir(temp_dir)
""".replace('\n', '\\n'),
    "post_code": """
os.chdir(__current)
""".replace('\n', '\\n'),
    "error_message": """
    If you see this message, then the image was
    not created or loaded properly. This sometimes happens when creating
    a figure for the first time. Try reloading it or, if it does not work,
    generating the image again.
    """.replace('\n', '') }

    load_image = """
function load_image(uid, image_name){
var j = new XMLHttpRequest();
img = document.getElementById('img_'+uid);
var now = new Date();
img.src = "/generated_image"+now.getTime()+"?url="+image_name;
}
"""

    # We clean up the directory before the first use
    # to remove all old images; this is not strictly needed, but will
    # help to prevent cluttering.
    if not page.includes("image_included"):
        page.add_include("image_included")
        page.add_js_code(image_jscode)
        page.add_js_code(load_image)
        old_files = [x for x in os.listdir(defaults.temp_dir)]
        for x in old_files:
            print "removing file %s"%(x)
            try:
                os.remove(os.path.join(defaults.temp_dir, x))
            except:  # if it fails, it is not a major problem
                print "could not remove file %s"%(x)

