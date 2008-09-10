'''

c_turtle_js.py

Javascript based frontend for c_turtle.py; intended to be used with Crunchy
inside an html <canvas>.
'''

import math as _math

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin
from src.imports.c_turtle import CTurtle

# Since there can be many drawing areas (& Python interpreters) on a given
# page, we need to be able to keep track of relevant variables for each
# separately
_created_uids = []
_heights = {} # created canvas heights
_widths = {} # created canvas widths
_turtles = {} # created turtles in given canvas

class Turtle(CTurtle):
    def __init__(self, x=0, y=0, angle=0,
        visible=True, pen_down=True,
        shell_color='DarkGreen', shell_radius=20,
        head_color='Tan', head_radius=8, head_dist=25,
        legs_color='Tan', legs_radius=8, legs_dist=22,
        eyes_color='DarkGreen', eyes_radius=2, size_scaling=1 ):
        # line_drawings will include all the javascript instructions assigned
        # up to the time a new drawing is required, so that it can redraw
        # the entire set of lines, circles, etc.
        self.line_drawings = []
        CTurtle.__init__(self, x, y, angle, visible)
        self.default_colors()
        self.uid = plugin['get_uid']() # determining to which canvas it will be drawn
        if self.uid in _turtles:
            _turtles[self.uid].append(self)
        else:
            _turtles[self.uid] = [self]

        # physical appearance
        self.shell_color = shell_color
        self.shell_radius = shell_radius * size_scaling
        self.head_color = head_color
        self.head_radius = head_radius * size_scaling
        self.head_dist = head_dist * size_scaling
        self.legs_color = legs_color
        self.legs_radius = legs_radius * size_scaling
        self.legs_dist = legs_dist * size_scaling
        self.eyes_color = eyes_color
        self.eyes_radius = eyes_radius *size_scaling
        self.eyes_dist = self.head_dist + self.head_radius/2.
        self.eyes_angle = 0.75 * _math.degrees(
                            _math.atan(1.0*self.head_radius/self.head_dist))
        if self._visible:
            _update_drawing()

    def goto(self, x, y): # tested
        '''Moves turtle to specified coordinates, without changing its
        orientation'''
        # draw line then move...
        if self._drawing:
            self.draw_line((self._x, self._y), (x, y))
        CTurtle.goto(self, x, y)
        _update_drawing()
    setpos = goto
    setposition = goto

    def default_colors(self):
        """sets the default line color and fill color"""
        CTurtle.default_colors(self)
        self.color(self._line_color)
        self.fill_color(self._fill_color)

    def home(self): # tested
        if self._drawing:
            self.draw_line((self._x, self._y), (0, 0))
        CTurtle.home(self)
        _update_drawing()

    def draw_line(self, from_point, to_point):
        self.line_drawings.append(line(from_point, to_point))

    def left(self, angle): # tested
        CTurtle.left(self, angle)
        _update_drawing()

    def right(self, angle): # tested
        CTurtle.right(self, angle)
        _update_drawing()

    def setheading(self, angle): # tested
        CTurtle.setheading(self, angle)
        _update_drawing()

    def draw(self, draw_last=False):
        '''draws a turtle'''

        plugin['exec_js'](plugin['get_pageid'](), ''.join(self.line_drawings))

        if not self._visible:
            return
        def x(angle):
            return _math.cos(_math.radians(angle + self._angle))
        def y(angle):
            return _math.sin(_math.radians(angle + self._angle))

        saved_fill_color = self._fill_color
        set_fill_color(self.legs_color)
        for i in [45, 135, 225, 315]:
            filled_circle((self._x + self.legs_dist*x(i),
                           self._y + self.legs_dist*y(i)), self.legs_radius)
        #a head of sorts
        set_fill_color(self.head_color)
        filled_circle((self._x + self.head_dist*x(0),
                       self._y + self.head_dist*y(0)), self.head_radius)
        #and a nice shell
        set_fill_color(self.shell_color)
        filled_circle((self._x, self._y), self.shell_radius)
        # two eyes
        set_fill_color(self.eyes_color)
        for i in [-self.eyes_angle, self.eyes_angle]:
            filled_circle((self._x + self.eyes_dist*x(i),
                           self._y + self.eyes_dist*y(i)), self.eyes_radius)
        set_fill_color(saved_fill_color)

    def color(self, col):
        CTurtle.color(self, col)
        self.line_drawings.append(_set_line_colour(self._line_color))
    colour = color
    set_line_color = color
    set_line_colour = color

def _update_drawing():
    uid = plugin['get_uid']()
    any_visible = False
    for turtle in _turtles[uid]:
        if turtle._visible:
            any_visible = True
            break
    if any_visible:
        _clear_world(uid)
    for turtle in _turtles[uid]:
        turtle.draw()

# Note: the normal <canvas> convention is to have the origin at the top left
# corner.  We will use a convention where the origin is at the bottom left
# corner, which means we need to convert y-coordinates in various
# functions.

global default_turtle
default_turtle = None
class World(object):
    def __init__(self, width=600, height=600, border_color='red', empty=True):
        '''creates a world in which a turtle can be made to move.
        global default_turtle

        This world is an html <canvas>'''
        uid = plugin['get_uid']()
        _heights[uid] = height
        _widths[uid] = width

        if uid not in _created_uids: # dynamically create a canvas
            _created_uids.append(uid)
            plugin['exec_js'](plugin['get_pageid'](), """var divCanvas = document.getElementById("div_%s");
                            var newCanvas = document.createElement("canvas");
                            newCanvas.setAttribute('id', 'canvas_%s')
                            divCanvas.appendChild(newCanvas);
            """%(uid, uid))
        plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").width=%d;
                        document.getElementById("canvas_%s").height=%d;
                        document.getElementById("canvas_%s").style.display = "block";
                        document.getElementById("canvas_%s").getContext('2d').clearRect(0, 0, %d, %d);
                        """ % (uid, width, uid, height, uid, uid, width, height))
        set_fill_colour('white')
        _filled_rectangle((0, 0), width, height)
        _set_line_colour('%s'%border_color)
        _rectangle((0, 0), width, height)
        _set_line_colour('black')
        self.width = width
        self.height = height
        if not empty and default_turtle is None:
            self.default_turtle = Turtle()

    def goto(self, x, y):
        self.default_turtle.goto(x, y)

    def clear_world(self):
        print('clearing world')
        set_fill_colour('yellow')
        _filled_rectangle((1, 1), self.width-2, self.height-2)

# useful synonym for beginners.
restart = World.__init__

def goto(x, y):
    global default_turtle
    if default_turtle is None:
        default_turtle = Turtle()
    default_turtle.goto(x, y)

def _clear_world(uid):
    set_fill_colour('white')
    _filled_rectangle((0, 0), _widths[uid], _heights[uid])
    _set_line_colour('red')
    _rectangle((0, 0), _widths[uid], _heights[uid])

def remove_world():
    '''remove existing graphics canvas from a page'''
    create-world(width=0, height=0, draw_turtle=False)

def _set_line_colour(col):
    '''Sets the default line colour using a valid value given as a string.'''
    # line_color & fill_color are variables whose values are associated with
    # a given canvas Context - we don't need to remember them.
    uid = plugin['get_uid']()
    instructions = """document.getElementById("canvas_%s").getContext('2d').strokeStyle = %r;""" % (uid, col)
    return instructions

_set_line_color = _set_line_colour # American spelling == British/Canadian spelling

def set_fill_colour(col):
    '''Sets the default fill colour using a valid value given as a string.'''
    # line_color & fill_color are variables whose values are associated with
    # a given canvas Context - we don't need to remember them.
    uid = plugin['get_uid']()
    #if not __validate_colour(col):
    #    col = "DeepPink" # make it stand out for now
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').fillStyle = %r;""" % (uid, col))
set_fill_color = set_fill_colour

def __translate_x(x, uid):
    '''translate x coordinates to that the origin coincides with the centre
       of the drawing area'''
    return x + _widths[uid]/2

def __translate_y(y, uid):
    '''translate y coordinates to that the origin coincides with the centre
       of the drawing area with positive direction being up'''
    return _heights[uid]/2 - y

def line(point_1, point_2):
    '''Draws a line from point_1 = (x1, y1) to point_2 (x2, y2) in the default line colour.'''
    uid = plugin['get_uid']()
    x1, y1 = point_1
    x2, y2 = point_2
    x1 = __translate_x(x1, uid)
    x2 = __translate_x(x2, uid)
    y1 = __translate_y(y1, uid)
    y2 = __translate_y(y2, uid)
    instructions = """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x1, y1, uid, x2, y2, uid)
    #plugin['exec_js'](plugin['get_pageid'](), instructions)
    return instructions

def circle(centre, r):
    '''Draws a circle of radius r centred on centre = (x, y) in the default line colour.'''
    uid = plugin['get_uid']()
    x, y = centre
    x = __translate_x(x, uid)
    y = __translate_y(y, uid)
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').arc(%s, %s, %s, 0, Math.PI*2, true);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x, y, r, uid))

def filled_circle(centre, r):
    '''Draws a filled circle of radius r centred on centre = (x, y) in the default fill colour.'''
    uid = plugin['get_uid']()
    x, y = centre
    x = __translate_x(x, uid)
    y = __translate_y(y, uid)
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').arc(%s, %s, %s, 0, Math.PI*2, true);
                             document.getElementById("canvas_%s").getContext('2d').fill();""" % (uid, uid, x, y, r, uid))

def _rectangle(corner, w, h):
    '''Draws a rectangle in the default line colour in normal canvas coordinates.'''
    uid = plugin['get_uid']()
    x, y = corner # bottom left
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').strokeRect(%s, %s, %s, %s);""" % (uid, x, y, w, h))

def _filled_rectangle(corner, w, h):
    '''Draws a filled rectangle in the default fill colour in normal canvas coordinates.'''
    uid = plugin['get_uid']()
    x, y = corner # bottom left
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').fillRect(%s, %s, %s, %s);""" % (uid, x, y, w, h))

def __point(x, y):
    '''Draws a point in the default line colour.'''
    uid = plugin['get_uid']()
    x = __translate_x(x, uid)
    y = __translate_y(y, uid)
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("canvas_%s").getContext('2d').beginPath();
                             document.getElementById("canvas_%s").getContext('2d').moveTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').lineTo(%s, %s);
                             document.getElementById("canvas_%s").getContext('2d').stroke();""" % (uid, uid, x, y, uid, x+1, y+1, uid))
