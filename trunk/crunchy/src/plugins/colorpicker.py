'''
Intended to provide an interface to the color picker jquery plugin.

Inserts the required html and javascript content to include it.
'''

from src.interface import plugin
from src.security import specific_allowed

def register():
    '''registers tag handlers for popup helpers'''
    plugin['register_tag_handler']("div", "title", "colorpicker", insert_colorpicker)

def insert_colorpicker(page, elem, uid):
    '''inserts the required javascript and css'''

    if not page.includes("jquery.colorpicker.js"):
        page.add_include("jquery.colorpicker.js")
        page.insert_js_file("/javascript/colorpicker/js/colorpicker.js")
        page.insert_css_file("/javascript/colorpicker/css/colorpicker.css")

    uid = "colorpicker_%s" % uid
    if 'class' in elem.attrib:
        elem.attrib['class'] += ' %s' % uid
    else:
        elem.attrib['class'] = uid
    elem.text = ''
    page.add_js_code(js_code_picker % uid)
    #if 'rel' in elem.attrib:
    #    if ' ' not in elem.attrib['rel']:
    #        # pull a single page using ajax...
    #        page.add_js_code(js_code_rel % (elem.tag, uid))
    #    else:
    #        # pull multiple pages using ajax...
    #        paths = elem.attrib['rel'].split(' ')
    #        args = ""
    #        for path in paths:
    #            if path: # multiple spaces will result in null strings
    #                args += "'%s', " % path
    #        args = args[:-2] # removed trailing comma
    #        page.add_js_code(js_code_multiple % (uid, elem.tag, uid, uid, args))
    #else:
    #    # use info from title element
    #    page.add_js_code(js_code_title % (elem.tag, uid))

js_code_picker = """
$(document).ready(function() {
  $('div.%s').ColorPicker({flat: true});
});"""
