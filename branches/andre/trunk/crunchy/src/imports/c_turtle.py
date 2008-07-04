'''
c_turtle.py

c_turtle  (pronounced "sea turtle", and where the "c" stands for "crunchy") is
a module intended to be roughly compatible with the turtle.py module included
in the standard Python distribution, but which contains some useful
additions but one big omission: it does not draw anything!

By using various front-ends for its drawing code, c_turtle is meant to be
portable in a variety of environments.

To avoid re-inventing everything, a significant proportion of the code
has been simply copied from the standard turtle module with some
adaptations/inspirations from the xturtle.py module by Gregor Lindl.
It is, however, very different from that module - and can not be claimed
to derive from it.
'''

import math as _math

class CTurtle(object):

    def __init__(self, x=0, y=0, angle=0, visible=True): # tested indirectly
        self._x = x
        self._y = y
        self._angle = angle
        self.degrees()
        self.default_colors()
        self._drawing = True
        self._visible = visible
        self._line_width = 1.0
        return

    def home(self):  # tested
        """resets the position to (0, 0) and orientation (angle) to 0.
        """
        self._angle = 0.0
        self._x = 0.0
        self._y = 0.0

    def degrees(self, fullcircle=360.0):  # tested
        """ Set angle measurement units to degrees.
        """
        # Don't try to change _angle if it is 0, because
        # _fullcircle might not be set, yet
        if self._angle:
            self._angle = (self._angle / self._fullcircle) * fullcircle
        self._fullcircle = fullcircle
        self._invradian = _math.pi / (fullcircle * 0.5)

    def radians(self):  # tested
        """ Set the angle measurement units to radians.
        """
        self.degrees(2.0*_math.pi)

    def default_colors(self):  # tested indirectly
        """sets the default line color and fill color"""
        self._line_color = 'black'
        self._fill_color = 'white'
        self._background_color = 'white'

    def width(self, number):  # tested
        """set the pen width"""
        self._line_width = number

    def visible(self, choice):  # tested
        """determine if the turtle is going to be drawn or not"""
        if choice in [True, False]:
            self._visible = choice
        else:
            self._visible = True

    def left(self, angle):  # tested
        """ Turn left angle units (units are by default degrees,
        but can be set via the degrees() and radians() functions.)
        """
        self._angle = (self._angle + angle) % self._fullcircle

    def right(self, angle):  # tested
        """ Turn right angle units (units are by default degrees,
        but can be set via the degrees() and radians() functions.)
        """
        self.left(-angle)

    def goto(self, x, y):  # tested
        '''goto or setposition or setpos: moves turtle to specified coordinates,
        without changing its orientation'''
        self._x, self._y = x, y
    setpos = goto
    setposition = goto

    def forward(self, len):  # tested
        '''forward or fd: sends turtle forward'''
        delta_x = len * _math.cos(_math.radians(self._angle))
        delta_y = len * _math.sin(_math.radians(self._angle))
        self.goto(self._x + delta_x, self._y + delta_y)
    fd = forward

    def backward(self, len):  # tested
        '''backward or backw or bk:
           sends turtle backward, keeping same orientation'''
        self.forward(-len)
    back = backward
    bk = backward

    def heading(self):  # tested
        """ Return the turtle's current heading.
        """
        return self._angle

    def setheading(self, angle):  # tested
        """ Set the turtle facing the given angle.

        Here are some common directions in degrees:
           0 - east
          90 - north
         180 - west
         270 - south
        """
        self._angle = angle

    def setx(self, xpos):  # tested
        """ Set the turtle's x coordinate to be xpos."""
        self.goto(xpos, self._y)

    def sety(self, ypos):  # tested
        """ Set the turtle's y coordinate to be ypos."""
        self.goto(self._x, ypos)

    def position(self):  # tested
        """ Return the current [x, y] location of the turtle as a list
        """
        return [self._x, self._y]

    def towards(self, *args):  # tested
        """Returs the angle, which corresponds to the line
        from turtle-position to point (x,y).

        Argument can be two coordinates or one pair of coordinates
        or a CTurtle instance.
        """
        if len(args) == 2:
            x, y = args
        else:
            arg = args[0]
            if isinstance(arg, CTurtle):
                x, y = arg._x, arg._y
            else:
                x, y = arg
        dx = x - self._x
        dy = y - self._y
        return (_math.atan2(dy,dx) / self._invradian) % self._fullcircle

    def penup(self):  # tested
        """penup or pen_up or pu or up:

           pull the pen up -- no drawing when moving.
        """
        if not self._drawing:
            return
        self._drawing = False
    pen_up = penup
    pu = penup
    up = penup

    def pendown(self):  # tested
        """pendown or pen_down or pd or down:

           push the pen down -- draws when moving.
        """
        if self._drawing:
            return
        self._drawing = True
    pen_down = pendown
    pd = pendown
    down = pendown

    def color(self, *args):  # tested
        """ color or colour or set_line_color or set_line_colour:

            set the pen color.

        Three input formats are allowed:

            color(s)
            s is a named color string, such as "red" or "yellow"

            color((r, g, b))
            *a tuple* of r, g, and b, which represent, an RGB color,
            and each of r, g, and b are in the range [0..1]

            color(r, g, b)
            r, g, and b represent an RGB color, and each of r, g, and b
            are in the range [0..1]

        Example:

        >>> turtle.color('brown')
        >>> tup = (0.2, 0.8, 0.55)
        >>> turtle.color(tup)
        >>> turtle.color(0, .5, 0)
        """
        self._line_color = self._parse_color(*args)
        return
    colour = color
    set_line_color = color
    set_line_colour = color

    def fill_color(self, *args):
        """ fill_color or fill_colour or set_fill_color or set_fill_colour:

            set the pen (fill) color

        Three input formats are allowed:

            fill_color(s)
            s is a named color string, such as "red" or "yellow"

            fill_color((r, g, b))
            *a tuple* of r, g, and b, which represent, an RGB color,
            and each of r, g, and b are in the range [0..1]

            fill_color(r, g, b)
            r, g, and b represent an RGB color, and each of r, g, and b
            are in the range [0..1]

        Example:

        >>> turtle.fill_color('brown')
        >>> tup = (0.2, 0.8, 0.55)
        >>> turtle.fill_color(tup)
        >>> turtle._fillcolor(0, .5, 0)
        """
        self._fill_color = self._parse_color(*args)
        return
    colour = color
    set_line_color = color
    set_line_colour = color

    def background(self, *args):
        """ background: set the background color

        Three input formats are allowed:

            fill_color(s)
            s is a named color string, such as "red" or "yellow"

            fill_color((r, g, b))
            *a tuple* of r, g, and b, which represent, an RGB color,
            and each of r, g, and b are in the range [0..1]

            fill_color(r, g, b)
            r, g, and b represent an RGB color, and each of r, g, and b
            are in the range [0..1]

        Example:

        >>> turtle.fill_color('brown')
        >>> tup = (0.2, 0.8, 0.55)
        >>> turtle.fill_color(tup)
        >>> turtle._fillcolor(0, .5, 0)
        """
        self._background_color = self._parse_color(*args)
        return

    def _parse_color(self, *args):  # tested
        """ does the parsing for color(), set_fill_colour(), background()
            and their various synonyms"""
        if not args:
            return 'black'
        if len(args) == 1:
            color = args[0]
            if type(color) == type(""):
                # Test the color first
                return color
            try:
                r, g, b = color
            except:
                return 'black'
        else:
            try:
                r, g, b = args
            except:
                return 'black'
        try:
            assert 0 <= r <= 1
            assert 0 <= g <= 1
            assert 0 <= b <= 1
        except:
            return 'black'
        x = 255.0
        y = 0.5
        return "#%02x%02x%02x" % (int(r*x+y), int(g*x+y), int(b*x+y))

    # the following are implementation specific
    def begin_fill(self):
        pass
    def end_fill(self):
        pass
    def circle(self, radius, extent=None):
        pass
    def delay(self, dt):
        pass
    def speed(self, speed):
        pass
