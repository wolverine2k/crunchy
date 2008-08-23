'''
Inserts the required jquery-based javascript for animating the sidebar menu.
'''

from src.interface import plugin

def register():
    '''registers a simple tag handler'''
    plugin['register_tag_handler']("div", "id", "crunchy_sidebar", insert_javascript)

def insert_javascript(page, elem, dummy):
    '''inserts the required javascript to animate the menu'''
    page.insert_js_file("/javascript/jquery.dimensions.js")
    page.insert_js_file("/javascript/jquery.accordion.js")
    page.add_js_code(js_code)

js_code = """
$(function () {
  $('ul.categories').accordion({
    // the drawer handle
    header: 'span.heading',

    // our selected class
    selectedClass: 'open',

    // match the Apple slide out effect
    event: 'mouseover'
  });
});"""
