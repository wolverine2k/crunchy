"""
graphics.py
"""

import threading

import CrunchyPlugin as __cp

def register():
    # no callbacks to register or initialisation needed
    pass

def init_graphics():
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").style.display = "block";
                             document.getElementById("canvas_%s").getContext('2d').clearRect(0, 0, 400, 400);
                          """ % (uid, uid))
    
def set_line_colour(col):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').strokeStyle = %r;""" % (uid, col))
    
def set_fill_colour(col):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').fillStyle = %r;""" % (uid, col))
    
def line((x1, y1), (x2, y2)):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x1, y1, uid, x2, y2, uid))

def circle((x, y), r):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').arc(%s, %s, %s, 0, Math.PI*2, true);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x, y, r, uid))
    
def filled_circle((x, y), r):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').arc(%s, %s, %s, 0, Math.PI*2, true);
                             document.getElementById("canvas_%s").getContext('2d').fill();""" % (uid, uid, x, y, r, uid))
    
def rectangle((x1, y1), w, h):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').strokeRect(%s, %s, %s, %s);""" % (uid, x1, y1, w, h))
    
def filled_rectangle((x1, y1), w, h):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').fillRect(%s, %s, %s, %s);""" % (uid, x1, y1, w, h))
    
def triangle((x1, y1), (x2, y2), (x3, y3)):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').closePath();
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x1, y1, uid, x2, y2, uid, x3, y3, uid, uid))
    
def filled_triangle((x1, y1), (x2, y2), (x3, y3)):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').closePath();
                             document.getElementById("canvas_%s").getContext('2d').fill();""" % (uid, uid, x1, y1, uid, x2, y2, uid, x3, y3, uid, uid))
    
def point(x, y):
    uid = __cp.get_uid()
    __cp.exec_js(__cp.get_pageid(), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x, y, uid, x+1, y+1, uid))
