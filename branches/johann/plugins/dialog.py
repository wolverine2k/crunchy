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
        dialogs[self.uid] = self
        self.data = {}
        self.event = threading.Event()
        
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
    dialogs[request.args["form_id"]].event.set()
    
def run_dialog(d):
    """runs a dialog in the current output widget and returns a dictionary of names:values,
    blocks execution until the dialog is finished."""
    io_id = get_uid()
    fid = "form_" + io_id
    dialog_html = """<div id="%s">%s<p><button onclick="window.sendForm('%s')">%s</button></p></div>""" %(fid,d.get_HTML(), fid, "OK")
    append_html(get_pageid(), io_id, dialog_html)
    exec_js(get_pageid(),dialog_js)
    d.event.wait()
    return d.data

dialog_js = r"""
window.sendForm = function sendForm(fid) {
        alert(fid);
        var formEl = document.getElementById(fid);
        var inputs = formEl.getElementsByTagName('input');
        var req_buf = "";
        for(i=0;i<inputs.length;i++) {
            var iName = inputs[i].name;
            var iVal = inputs[i].value;
            req_buf += (encodeURIComponent(iName) + '=' + encodeURIComponent(iVal) + '&');
        }
        var sels = formEl.getElementsByTagName('select');
        for(i=0;i<sels.length;i++) {
            var iName = sels[i].name;
            var iVal = sels[i].value;
            req_buf += (encodeURIComponent(iName) + '=' + encodeURIComponent(iVal) + '&');
        }
        var req = new XMLHttpRequest();
        req.open("POST", "/dialog?form_id="+fid, false);
        req.send(req_data);
        formEl.style.display = "none";
    }
"""