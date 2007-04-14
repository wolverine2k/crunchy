"""
graphics.py
"""

import threading

from cometIO import output_queue
from CQueue import QueueableMergeable as QBLM

def init_graphics():
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('init_graphics("%s");' % uid, "JSCRIPT", "ALL"))
    
def set_line_colour(col):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('set_line_colour("%s", "%s");' % (uid, col), "JSCRIPT", "ALL"))
    
def set_fill_colour(col):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('set_fill_colour("%s", "%s");' % (uid, col), "JSCRIPT", "ALL"))
    
def line((x1, y1), (x2, y2)):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('draw_line("%s", %s, %s, %s, %s);' % (uid, x1, y1, x2, y2), "JSCRIPT", "ALL"))

def circle((x, y), r):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('circle_stroke("%s", %s, %s, %s);' % (uid, x, y, r), "JSCRIPT", "ALL"))
    
def filled_circle((x, y), r):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('circle_fill("%s", %s, %s, %s);' % (uid, x, y, r), "JSCRIPT", "ALL"))
    
def rectangle((x1, y1), w, h):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('rectangle_stroke("%s", %s, %s, %s, %s);' % (uid, x1, y1, w, h), "JSCRIPT", "ALL"))
    
def filled_rectangle((x1, y1), w, h):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('rectangle_fill("%s", %s, %s, %s, %s);' % (uid, x1, y1, w, h), "JSCRIPT", "ALL"))
    
def triangle((x1, y1), (x2, y2), (x3, y3)):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('triangle_stroke("%s", %s, %s, %s, %s, %s, %s);' % (uid, x1, y1, x2, y2, x3, y3), "JSCRIPT", "ALL"))
    
def filled_triangle((x1, y1), (x2, y2), (x3, y3)):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('triangle_fill("%s", %s, %s, %s, %s, %s, %s);' % (uid, x1, y1, x2, y2, x3, y3), "JSCRIPT", "ALL"))
    
def point(x, y):
    uid = threading.currentThread().getName()
    output_queue.put(QBLM('draw_line("%s", %s, %s, %s, %s);' % (uid, x, y, x+1, y+1), "JSCRIPT", "ALL"))
