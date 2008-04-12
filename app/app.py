from System import EventHandler, Action
from System.Windows.Browser.HtmlPage import Document, Window
from System.Threading import Thread, ThreadStart, EventWaitHandle, AutoResetEvent, Monitor
from System.Collections.Generic import Queue
from System.ComponentModel import BackgroundWorker, ProgressChangedEventHandler, DoWorkEventHandler

import sys
import traceback

import Widgets
from cross_browser import current_browser
from debug_client import send_debug

Document.test.innerHTML = "Here's a Python Interpreter to play with: (no support for stdin yet - I can't get threading to work nicely)"

t = Document.CreateElement("p")
t.innerHTML = "This is running on %s." % current_browser.description
t.SetStyleAttribute("color", "blue")
Document.Body.AppendChild(t)

switch_btn = Document.CreateElement("button")
Document.test.AppendChild(switch_btn)

curr_widget = None

def setup_editor(obj, args):
    global curr_widget
    try:
        switch_btn.DetachEvent("onclick", EventHandler(setup_editor))
    except:
        pass
    switch_btn.AttachEvent("onclick", EventHandler(setup_interp))
    switch_btn.innerHTML = "Switch to an Interpreter"
    if curr_widget != None:
        print "removing"
        curr_widget.remove()
        traceback.print_exc()
    try:
        curr_widget = Widgets.EditorWidget(Document.dipsy)
    except:
        Window.Alert(traceback.format_exc() + " ")
def setup_interp(obj, args):
    global curr_widget
    try:
        switch_btn.DetachEvent("onclick", EventHandler(setup_interp))
    except:
        pass
    switch_btn.AttachEvent("onclick", EventHandler(setup_editor))
    switch_btn.innerHTML = "Switch to an Editor"
    if curr_widget != None:
        curr_widget.remove()
    curr_widget = Widgets.Interpreter(Document.dipsy)

# initialise it all:
setup_interp(None, None)