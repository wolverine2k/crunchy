"""
math_graphics.py

Similar to graphics.py, except that the origin is at the bottom left
corner of the drawing region.
"""

import re

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin
import src.imports.graphics as graphics

validate_colour = graphics.validate_colour
set_line_colour = graphics.set_line_colour
set_line_color = set_line_colour
set_fill_colour = graphics.set_fill_colour
set_fill_color = set_fill_colour

created_uids = []
HEIGHTS = {}

def init_graphics(width=400, height=400, border_color='red'):
    uid = plugin['get_uid']()
    HEIGHTS[uid] = height
    if uid not in created_uids: # dynamically create a canvas
        created_uids.append(uid)
        plugin['exec_js'](plugin['get_pageid'](), """var divCanvas = document.getElementById("div_%s");
                        var newCanvas = document.createElement("canvas");
                        newCanvas.setAttribute('id', 'canvas_%s');
                        divCanvas.appendChild(newCanvas);
        """%(uid, uid))
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").width=%d;
                    document.getElementById("canvas_%s").height=%d;
                    document.getElementById("canvas_%s").style.display = "block";
                    document.getElementById("canvas_%s").getContext('2d').clearRect(0, 0, %d, %d);
                    """ % (uid, width, uid, height, uid, uid, width, height))
    set_line_colour('%s'%border_color)
    set_fill_colour('white')
    filled_rectangle((0, 0), width, height)
    rectangle((0, 0), width, height)
    set_line_colour('black')

def clear_graphics():
    '''remove existing graphics from a page'''
    init_graphics(0, 0)

def line(point_1, point_2):
    '''Draws a line from point_1 = (x1, y1) to point_2 (x2, y2) in the default line colour.'''
    uid = plugin['get_uid']()
    x1, y1 = point_1
    x2, y2 = point_2
    y1 = HEIGHTS[uid] - y1
    y2 = HEIGHTS[uid] - y2
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x1, y1, uid, x2, y2, uid))

def circle(centre, r):
    '''Draws a circle of radius r centred on centre = (x, y) in the default line colour.'''
    uid = plugin['get_uid']()
    x, y = centre
    y = HEIGHTS[uid] - y
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').arc(%s, %s, %s, 0, Math.PI*2, true);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x, y, r, uid))

def filled_circle(centre, r):
    '''Draws a filled circle of radius r centred on centre = (x, y) in the default fill colour.'''
    uid = plugin['get_uid']()
    x, y = centre
    y = HEIGHTS[uid] - y
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').arc(%s, %s, %s, 0, Math.PI*2, true);
                             document.getElementById("canvas_%s").getContext('2d').fill();""" % (uid, uid, x, y, r, uid))

def rectangle(corner, w, h):
    '''Draws a rectangle in the default line colour.'''
    uid = plugin['get_uid']()
    x, y = corner # bottom left
    y = HEIGHTS[uid] - y - h
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').strokeRect(%s, %s, %s, %s);""" % (uid, x, y, w, h))

def filled_rectangle(corner, w, h):
    '''Draws a filled rectangle in the default fill colour.'''
    uid = plugin['get_uid']()
    x, y = corner # bottom left
    y = HEIGHTS[uid] - y - h
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').fillRect(%s, %s, %s, %s);""" % (uid, x, y, w, h))

def triangle(point_1, point_2, point_3):
    '''Draws a triangle joining the three points in the default line colour.'''
    uid = plugin['get_uid']()
    x1, y1 = point_1
    x2, y2 = point_2
    x3, y3 = point_3
    y1 = HEIGHTS[uid] - y1
    y2 = HEIGHTS[uid] - y2
    y3 = HEIGHTS[uid] - y3
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').closePath();
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x1, y1, uid, x2, y2, uid, x3, y3, uid, uid))

def filled_triangle(point_1, point_2, point_3):
    '''Draws a filled triangle joining the three points in the default fill colour.'''
    uid = plugin['get_uid']()
    x1, y1 = point_1
    x2, y2 = point_2
    x3, y3 = point_3
    y1 = HEIGHTS[uid] - y1
    y2 = HEIGHTS[uid] - y2
    y3 = HEIGHTS[uid] - y3
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').closePath();
                             document.getElementById("canvas_%s").getContext('2d').fill();""" % (uid, uid, x1, y1, uid, x2, y2, uid, x3, y3, uid, uid))

def point(x, y):
    '''Draws a point in the default line colour.'''
    uid = plugin['get_uid']()
    y = HEIGHTS[uid] - y
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x, y, uid, x+1, y+1, uid))


