# -*- coding: utf-8 -*-
''' graphics.py
Andre Roberge
Class and utility function used to process graphics within a <canvas> tag.
'''

import re

class Graphics(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.js_code = ["""
            ctx.clearRect(0, 0, %d, %d);
            ctx.strokeStyle="red";
            ctx.fillStyle="red";
            ctx.beginPath();
            ctx.arc(1, 1, 2, 0, Math.PI*2, false);
            ctx.fill();
            ctx.strokeStyle="black";
            ctx.fillStyle="black";
            """%(width, height)]

    def set_line_colour(self, col):
        if validate_colour(col):
            self.js_code.append('ctx.strokeStyle="%s";'%col)
        else:
            raise   # for now
        return
        
    def set_fill_colour(self, col):
        if validate_colour(col):
            self.js_code.append('ctx.fillStyle="%s";'%col)
        else:
            raise   # for now
        return

    def line(self, (x, y), (x2, y2)):
        self.js_code.append("ctx.beginPath();"+
            "ctx.moveTo(%f, %f);"%(x, y) + "ctx.lineTo(%f, %f);"%(x2, y2) +
            "ctx.stroke();")
        return

    def circle(self, (x, y), radius):
        self.js_code.append("ctx.beginPath();" +
            "ctx.arc(%f, %f, %f, 0, Math.PI*2, true);"%(x, y, radius) +
            "ctx.stroke();")
        return

    def filled_circle(self, (x, y), radius):
        self.js_code.append("ctx.beginPath();"+
            "ctx.arc(%f, %f, %f, 0, Math.PI*2, true);"%(x, y, radius) +
            "ctx.fill();")
        return

    def rectangle(self, (x, y), width, height):
        self.js_code.append("ctx.strokeRect(%f, %f, %f, %f);"%
                                (x, y, width, height))
        return

    def filled_rectangle(self, (x, y), width, height):
        self.js_code.append("ctx.fillRect(%f, %f, %f, %f);"%
                                (x, y, width, height))
        return

    def _triangle(self, (x1, y1), (x2, y2), (x3, y3), style):
        self.js_code.append("ctx.beginPath();"+
            "ctx.moveTo(%f, %f);"%(x1, y1) + "ctx.lineTo(%f, %f);"%(x2, y2) +
            "ctx.lineTo(%f, %f);"%(x3, y3) + "ctx.closePath();" +
            "ctx.%s();"%style )
        return

    def triangle(self, (x1, y1), (x2, y2), (x3, y3)):
        return self._triangle((x1, y1), (x2, y2), (x3, y3), 'stroke')

    def filled_triangle(self, (x1, y1), (x2, y2), (x3, y3)):
        return self._triangle((x1, y1), (x2, y2), (x3, y3), 'fill')

    def point(self, x, y):
        self.line((x, y), (x + 1, y+1)) 
        return

class Plot(Graphics):
    # note: axis follow math convention, origin at bottom of graph
    def __init__(self, width, height):
        self.width = width*1.0 
        self.height = height*1.0
        self.js_code = ["""
            ctx.clearRect(0, 0, %d, %d);
            ctx.strokeStyle="black";
            ctx.fillStyle="black";
            """%(width, height) ]
        self.x_axis_offset = 15.
        self.y_axis_offset = 15.
        self.x_min = 0.
        self.y_min = 0.
        self.x_max = self.width
        self.y_max = self.height
        self.x_scale = 1.
        self.y_scale = 1.
    
    def _x_rescale(self, x):
        x -= self.x_min
        x *= self.x_scale
        return x
    
    def _y_rescale(self, y):
        y -= self.y_min
        y *= self.y_scale
        return y

    def line(self, (x, y), (x2, y2)):
        x = self._x_rescale(x)
        y = self._y_rescale(y)
        x2 = self._x_rescale(x2)
        y2 = self._y_rescale(y2)
        return Graphics.line(self, (x, y), (x2, y2))

    def arrow(self, (x1, y1), (x2, y2), (x3, y3)):
        x1 = self._x_rescale(x1)
        x2 = self._x_rescale(x2)
        x3 = self._x_rescale(x3)
        y1 = self._y_rescale(y1)
        y2 = self._y_rescale(y2)
        y3 = self._y_rescale(y3)
        return Graphics._triangle(self, (x1, y1), (x2, y2), (x3, y3), 'stroke')

    def set_xrange(self, x_min, x_max):
        self.x_axis_offset *= self.x_scale # reverts to original value
        self.x_min = x_min
        self.x_max = x_max
        self.x_scale = self.width/(x_max - x_min)
        self.x_axis_offset /= self.x_scale

    def set_yrange(self, y_min, y_max):
        # values of y_max and y_min reversed so that the graph is drawn
        # with the usual math convention.
        self.y_axis_offset *= self.y_scale 
        self.y_min = y_max
        self.y_max = y_min
        self.y_scale = self.height/(y_min - y_max) # "direction": usually negative here
        self.y_axis_offset /= abs(self.y_scale)

    def x_axis(self, pos='middle'):
        x_min = self.x_min + self.x_axis_offset
        if pos=='middle':
            y = (self.y_max + self.y_min)/2.
        elif pos=='top':
            y = self.y_min + 1./self.y_scale
        elif pos=='bottom':
            y = self.y_max - 1./self.y_scale
        else:
            raise  # for now
        self.line((x_min, y), (self.x_max, y))
        x = self.x_max - self.x_axis_offset*0.5
        y1 = y - self.y_axis_offset*0.5
        y2 = y + self.y_axis_offset*0.5
        self.arrow((self.x_max, y), (x, y1), (x, y2))
        return

    def y_axis(self, pos='left'):
        if pos=='middle':
            x = (self.x_max + self.x_min)/2.
        elif pos=='left':
            x = self.x_min + self.x_axis_offset
        else:
            raise  # for now
        self.line((x, self.y_min), (x, self.y_max))
        y = self.y_min - self.y_axis_offset*0.5
        x1 = x - self.x_axis_offset*0.5
        x2 = x + self.x_axis_offset*0.5
        self.arrow((x, self.y_min), (x1, y), (x2, y))
        return

    def prepare_graph(self, x_range=(0, 400), y_range=(0, 400), 
                      x_axis='middle', y_axis='left'):
        self.set_xrange(x_range[0], x_range[1])
        self.set_yrange(y_range[0], y_range[1])
        self.x_axis(x_axis)
        self.y_axis(y_axis)
        return
    
    def plot_function(self, fn):
        nb_points = int(self.width - 2*self.x_axis_offset*self.x_scale - 1)
        x_increment = (self.x_max - self.x_min)/self.width
        x2 = self.x_min
        y2 = fn(x2)
        for i in xrange(nb_points):
            x1 = x2
            y1 = y2
            x2 += x_increment
            y2 = fn(x2)
            self.line((x1+self.x_axis_offset, y1), (x2+self.x_axis_offset, y2))
        return

named_colour = re.compile('^[a-zA-Z]*[a-zA-Z]$') # only letters
hex_code = re.compile('^#[a-fA-F0-9]{5,5}[a-fA-F0-9]$') # begin with "#", then 6 hexadecimal values
rgb_pattern = re.compile('^rgb\s*\((.+?),(.+?),(.+?)\)$') #begins with rgb(, etc
rgba_pattern = re.compile('^rgba\s*\((.+?),(.+?),(.+?),(.+?)\)$')

def validate_colour(colour):
    colour = colour.strip()
    if hex_code.match(colour):
        return True
    elif named_colour.match(colour): # ; assume valid as colour name;
        return True           # javascript would treat it as black otherwise.
    elif rgb_pattern.match(colour):
        res = rgb_pattern.search(colour)
        try:
            r = int(res.groups()[0])
            g = int(res.groups()[1])
            b = int(res.groups()[2])
            if r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255:
                return True
            else:
                raise errors.ColourNameError(colour)
        except:
            raise errors.ColourNameError(colour)
    elif rgba_pattern.match(colour):
        res = rgba_pattern.search(colour)
        try:
            r = int(res.groups()[0])
            g = int(res.groups()[1])
            b = int(res.groups()[2])
            a = float(res.groups()[3])
            if r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255 \
                and a >= 0. and a <= 1.0:
                return True
            else:
                raise errors.ColourNameError(colour)
        except:
            raise errors.ColourNameError(colour)
    raise errors.ColourNameError(colour)

