"""A plugin that handles all the VLAM elements"""

from CrunchyPlugin import CrunchyPlugin

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

class VLAMElems(CrunchyPlugin):
    def register(self):
        self.register_vlam_handler("pre", "editor", self.insert_editor)
        self.register_vlam_handler("pre", "interpreter", self.insert_interpreter)
    
    def insert_editor(self, page, elem, uid):
        inp = et.SubElement(elem, "textarea")
        inp.attrib["rows"] = "10"
        inp.attrib["cols"] = "80"
        inp.attrib["id"] = "code_" + uid
        inp.text = "\n"
        et.SubElement(elem, "br")
        btn = et.SubElement(elem, "button")
        btn.attrib["onclick"] = "exec_code('%s')" % uid
        btn.text = "Execute"
        et.SubElement(elem, "br")
        page.insert_output(elem, uid)
        
    def insert_interpreter(self, page, elem, uid):
        """inserts an interpreter (actually the js code to initialise an interpreter)"""
        page.add_js_code('init_interp("%s");' % uid)
        page.insert_output(elem, uid)
    