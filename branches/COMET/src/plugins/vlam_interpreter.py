

from CrunchyPlugin import *

def register():
    register_vlam_handler("pre", "interpreter", insert_interpreter)
           
def insert_interpreter(page, elem, uid):
    """inserts an interpreter (actually the js code to initialise an interpreter)"""
    page.add_js_code('init_interp("%s");' % uid)
    page.insert_output(elem, uid)
    