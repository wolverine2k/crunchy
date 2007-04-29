"""Create dialogs in HTML using simple python code

inspired by Yusdi Santoso's WebLab - see:
http://physics.ox.ac.uk/users/santoso/Software.WebLab.html

This was initially based on Yusdi's version 0.0.4
"""

import threading
from cgi import parse_qs

from CrunchyPlugin import *


provides = set(["dialog"])

def register():
    register_http_handler("/dialog", dialog_handler)
    
# all the registered dialogs:
dialogs = {}

class Dialog(object):
    def __init__(self, title):
        global dialogs
        self.buf = ""
        self.title = title
        self.uid = gen_uid()
        dialogs[uid] = self
        self.data = {}
    def get_HTML(self):
        return '<div>' + self.buf + '</div>'
    
    def add_label(self, text):
        self.buf += "<p>%s</p>" % text
        
    def add_text_field(self, name, title, content):
        self.buf += '<p><label for="%s">%s</label><input type="text" name="%s" value = "%s" /></p>' % (name, title, name, content)
        
    def add_selection_box(self, name, title, options, selectedOpt=None):
        self.buf += '<p><label for="%s">%s</label><select name="%s">' %(name, title, name)
        for opt in options:
            isSelected = ''
            if opt == selectedOpt:
                isSelected = "selected='1'"
            self.buf += "<option %s> %s</option>" % (isSelected, opt)
        self.buf += "</select></p>"
        
def dialog_handler(request):
    global dialogs
    if request.args["form_id"] not in dialogs:
        return
    data = parse_qs(request.data, True)
    dialogs[request.args["form_id"]].data = data
def run_dialog(d):
    """runs a dialog in the current output widget and returns a dictionary of names:values,
    blocks execution until the dialog is finished."""
    uid = get_uid()
    