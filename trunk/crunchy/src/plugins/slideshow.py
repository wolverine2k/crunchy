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
    plugin['register_meta_handler']("content", insert_javascript)
    plugin['register_end_pagehandler'](insert_interactive_objects)
    plugin['register_tag_handler']("div", "class", "slide", set_overflow)

def insert_javascript(page, elem):
    '''inserts the required javascript for the slideshow and notes the fact
       that this is a slideshow.'''
    if 's5 1' not in elem.attrib['content'].lower():
        return
    if not page.includes("slideshow_included"):
        page.add_include("slideshow_included")
    if 's5 1.2' in elem.attrib['content'].lower():
        page.add_include("S5 version 1.2")

def set_overflow(page, elem, dummy):
    '''sets the proper overflow value for each slide.
    This allows interactive elements to produce output that would not
    normally fit on a slide to be seen by using the scrollbar.'''
    if not page.includes("slideshow_included"):
        return
    elem.attrib['style'] = "height: 70%; overflow: auto;"

def insert_interactive_objects(page):
    '''inserts the interactive objects required in a slideshow'''
    if not page.includes("slideshow_included"):
        return
    for div in page.tree.getiterator("div"):
        if 'class' in div.attrib:
            if div.attrib['class'] == "presentation":
                # add slide with interpreter
                new_div = Element("div")
                new_div.attrib['class'] = "slide"
                # new_div is not processed by set_overflow above which is why
                # we must set this property explictly.
                new_div.attrib['style'] = "height: 70%; overflow: auto;"
                new_div.attrib['id'] = "crunchy_interpreter"
                pre = SubElement(new_div, "pre", title="interpreter")
                # the following text is at least 50 characters
                # with a non-space character at the end.  This is to allow
                # the creation of a list with "short" titles to select
                # a given slide.
                # see slides.js line 100
                pre.text = "# Crunchy Interpreter                             #"
                uid = page.pageid + "_" + uidgen(page.username)
                plugin['services'].insert_interpreter(page, pre, uid)
                div.append(new_div)
                # add slide with editor
                new_div2 = Element("div")
                new_div2.attrib['class'] = "slide"
                # new_div2 is not processed by set_overflow above ...
                new_div2.attrib['style'] = "height: 70%; overflow: auto;"
                new_div2.attrib['id'] = "crunchy_editor"
                pre2 = SubElement(new_div2, "pre", title="editor")
                # same as above.
                pre2.text = "# Crunchy editor                                 #"
                uid = page.pageid + "_" + uidgen(page.username)
                plugin['services'].insert_editor(page, pre2, uid)
                div.append(new_div2)
                return