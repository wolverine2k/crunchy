Testing c_turtle.py
===================

This file contains essentially a (reformated) log of a TDD of c_turtle.py.

It has been tested with Python 2.4, 2.5, 3.0a1 and 3.0a2

We start by initializing a simple CTurtle.

    >>> import src.imports.c_turtle as c
    >>> t1 = c.CTurtle()
    >>> def get_int_pos(tortue):
    ...     return int(tortue._x), int(tortue._y), int(tortue._angle)
    ...
    >>> get_int_pos(t1)
    (0, 0, 0)


Next, we test some simple methods/functions.
    >>> t1.degrees()
    >>> t1._fullcircle, t1._invradian #doctest:+ELLIPSIS
    (360.0, 0.017453292...)
    >>> t1.radians()
    >>> t1._fullcircle, t1._invradian #doctest:+ELLIPSIS
    (6.283185..., 1.0)

Setting angles.

    >>> t1.degrees()
    >>> t1.left(45)
    >>> t1._angle
    45.0
    >>> t1.right(30)
    >>> t1._angle
    15.0
    >>> t1.setheading(5.0)
    >>> t1.heading()
    5.0

Moving.

    >>> t1.goto(5, 5)
    >>> get_int_pos(t1)
    (5, 5, 5)
    >>> t1.home()
    >>> get_int_pos(t1)
    (0, 0, 0)
    >>> t1.forward(100)
    >>> get_int_pos(t1)
    (100, 0, 0)
    >>> t1.backward(50)
    >>> get_int_pos(t1)
    (50, 0, 0)
    >>> t1.left(90)
    >>> t1.forward(50)
    >>> get_int_pos(t1)
    (50, 50, 90)
    >>> t1.setx(100)
    >>> get_int_pos(t1)
    (100, 50, 90)
    >>> t1.sety(100)
    >>> get_int_pos(t1)
    (100, 100, 90)
    >>> t1.position()
    [100, 100]
    
Testing some synonyms.

    >>> t1.home()
    >>> t1.fd(100)
    >>> get_int_pos(t1)
    (100, 0, 0)
    >>> t1.bk(50)
    >>> get_int_pos(t1)
    (50, 0, 0)
    >>> t1.back(40)
    >>> get_int_pos(t1)
    (10, 0, 0)
    >>> t1.setpos(100, 100)
    >>> get_int_pos(t1)
    (100, 100, 0)
    >>> t1.setpos(50, 50)
    >>> get_int_pos(t1)
    (50, 50, 0)

Testing advanced angles

    >>> t1.home()
    >>> t1.towards(50, 50)
    45.0
    >>> t2 = c.CTurtle()
    >>> t2.left(30.0)
    >>> t2.forward(10)
    >>> int(round(t1.towards(t2)))
    30
    >>> int(round(t2.towards(t1)))
    210
    
Testing pen up/down status, and line width

    >>> t1._drawing
    True
    >>> t1.penup()
    >>> t1._drawing
    False
    >>> t1.pendown()
    >>> t1._drawing
    True

    >>> t1.pen_up()
    >>> t1._drawing
    False
    >>> t1.pen_down()
    >>> t1._drawing
    True

    >>> t1.pu()
    >>> t1._drawing
    False
    >>> t1.pd()
    >>> t1._drawing
    True

    >>> t1.up()
    >>> t1._drawing
    False
    >>> t1.down()
    >>> t1._drawing
    True
    
    >>> t1.width(3.5)
    >>> t1._line_width
    3.5

Testing colors.

    >>> t1._parse_color(0, 0, 0)
    '#000000'
    >>> t1._parse_color(1, 1, 1)
    '#ffffff'
    >>> t1._parse_color(2, 1, 1)
    'black'
    >>> t1._parse_color((1, 0, 1))
    '#ff00ff'
    >>> t1._parse_color('red')
    'red'
    >>> t1.color('blue')
    >>> t1._line_color
    'blue'
    >>> t1.fill_color(0.5, 0.5, 0.5)
    >>> t1._fill_color
    '#808080'


    >>> t1.visible(True)
    >>> t1._visible
    True
    >>> t1.visible(False)
    >>> t1._visible
    False
    >>> t1.visible('dummy')
    >>> t1._visible
    True



