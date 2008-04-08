from System import EventHandler, Action
from System.Windows.Browser.HtmlPage import Document, Window
from System.Threading import Thread, ThreadStart, EventWaitHandle, AutoResetEvent, Monitor
from System.Collections.Generic import Queue
from System.ComponentModel import BackgroundWorker, ProgressChangedEventHandler, DoWorkEventHandler

import sys
import traceback

import Widgets

from debug_client import send_debug

Document.test.innerHTML = "Here's a Python Interpreter to play with: (no support for stdin yet - I can't get threading to work nicely)"

Widgets.Interpreter(Document.dipsy)