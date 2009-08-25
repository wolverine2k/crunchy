'''
slideshow plugin.

Enable the insertion of the javascript file required for S5 slide show, as
produced by docutils.

See http://docutils.sourceforge.net/docs/user/slide-shows.s5.html
'''

from src.interface import plugin, Element, SubElement
from src.utilities import uidgen

def register():
    '''registers a simple tag handler'''
    plugin['register_tag_handler']("meta", "content", "slideshow", insert_javascript)
    plugin['register_end_pagehandler'](insert_interactive_objects)

def insert_javascript(page, elem, dummy):
    '''inserts the required javascript for the slideshow'''
    if not page.includes("slideshow_included"):
        page.add_include("slideshow_included")
        page.insert_js_file("/javascript/slides.js")

def insert_interactive_objects(page):
    '''inserts the interactive objects required in a slideshow'''
    if not page.includes("slideshow_included"):
        return
    return
    for div in page.tree.getiterator("div"):
        if 'class' in div.attrib:
            if div.attrib['class'] == "presentation":
                new_div = Element("div")
                new_div.attrib['class'] = "slide"
                new_div.attrib['id'] = "crunchy_interpreter"
                pre = SubElement(new_div, "pre", title="interpreter")
                pre.text = "# Crunchy interpreter!"
                uid = page.pageid + "_" + uidgen(page.username)
                plugin['services'].insert_interpreter(page, pre, uid)
                div.append(new_div)
                return
