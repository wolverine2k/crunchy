'''
Plugin to convert lowercase text to uppercase
'''
# Created by Andrew Simmons (anjsimmo)
from src.interface import plugin

def register():
    '''register plugin for bold related tags'''
    for tag in ["b", "em", "strong"]:
        plugin['register_tag_handler'](tag, "title", "uppercase", insert_uppercase)

def insert_uppercase(page, elem, uid):
    '''convert to uppercase and add jQuery effect'''
    # Actual conversion to uppercase
    to_uppercase(elem)

    # Add jQuery effect

    # For interest, we will delay the effect proportionally to the length of
    # the first text node in this element
    delay = 150
    if elem.text:
        delay += len(elem.text * 250)

    # Add common code to document only once
    # Adapted from colorpicker,py
    if not page.includes("uppercaseEffect"):
        page.add_include("uppercaseEffect")
        page.add_js_code(js_uppercase_effect)
        page.add_css_code(css_uppercase_style)

    # Add unique code
    page.add_js_code(js_uppercase_delay % (uid, delay))

    # Add uid as class to make element accessible from jQuery
    # Copied from colorpicker.py
    if 'class' in elem.attrib:
        # append extra class (space separated)
        elem.attrib['class'] += ' %s' % uid
    else:
        # this is the first style
        elem.attrib['class'] = uid

def to_uppercase(elem):
    '''Convert text nodes to uppercase'''
    # Adapted from ElementTree.py itertext generator
    # Will traverse text nodes in order, but this is not really necessary
    if elem.text:
        elem.text = elem.text.upper()
    for e in elem:
        to_uppercase(e)
        if e.tail:
            e.tail = e.tail.upper()

js_uppercase_effect = """
function uppercaseEffect() {
  $(this).addClass('uppercase-style').fadeIn('slow');
}
"""

css_uppercase_style = """
.uppercase-style {color: #ff6644;}
"""

js_uppercase_delay = """
$(document).ready(function() {
  $('.%s').fadeOut(%s, uppercaseEffect);
});
"""
