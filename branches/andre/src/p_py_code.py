'''p_py_code.py

Plugin module whose purpose is simply to style Python code.

While its purpose is simple, it presents a few unusual options:
it can be called for two html elements (<pre>, <code>) with
two different vlam keywords (py_code, python_code), i.e. the following
four different combinations are valid calls for this plugin:
<pre title="py_code ...">
<pre title="python_code ...">
<code title="py_code ...">
<code title="python_code ...">
'''

import s_styler

# name(s) appearing in a vlam code for calling this plugin
name = ['py_code', 'python_code']
# valid html tags to which this element can be added
html_tags = ['pre', 'code']
# link to javascript file that needs to be included with this plugin
js_crunchy_link = None
js_chewy_link = None
# javascript code that needs to be included for each element added
js_crunchy = None
# javascript code that needs to be included for the markup tool
js_chewy = {'code': 'to be defined', 'pre': 'to be defined'}

def add_crunchy_markup(elem, id='ignored'):
    '''add the html markup to style the code'''
    if elem.tag in html_tags:
        python_code = s_styler.style(elem)
    else:
        raise Exception # needs to improve on this
    return None # we are not interested in the actual code

def add_chewy_markup(elem, id=None):
    pass # to be defined
