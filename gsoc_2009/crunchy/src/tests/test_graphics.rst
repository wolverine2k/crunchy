graphics.py tests
================================

graphics.py is a simple graphics module.  It has the following functions
that require testing:

#. `init()`_; see also: `init(origin at bottom)`_
#. `clear()`
#. `set_line_color()`_
#. `set_line_colour()`_
#. `set_fill_color()`_
#. `set_fill_colour()`_
#. `line()`_, `line()`_
#. `_circle()`_; see also: `_circle(origin at bottom)`_
#. `circle()`_; see also: `circle(origin at bottom)`_
#. `filled_circle()`_; see also: `filled_circle(origin at bottom)`_
#. `_rectangle()`_; see also: `_rectangle(origin at bottom)`_
#. `rectangle()`_; see also: `rectangle(origin at bottom)`_
#. `filled_rectangle()`_; see also: `filled_rectangle(origin at bottom)`_
#. `_triangle()`_; see also: `_triangle(origin at bottom)`_
#. `triangle()`_; see also: `triangle(origin at bottom)`_
#. `filled_triangle()`_; see also: `filled_triangle(origin at bottom)`_
#. `point()`_; see also: `point(origin at bottom)`_
#. `validate_colour()`_

Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

  >>> from src.interface import plugin
  >>> plugin.clear()
  >>> def get_uid():
  ...     return 'uid'
  >>> def get_pageid():
  ...     return 'pageid'
  >>> def exec_js(pid, js):
  ...     print(pid)
  ...     js = js.replace('document.getElementById', '') # makes lines shorter
  ...     js = js.replace('  ', '')
  ...     print9js.replace('.getContext', ''))
  >>> plugin['get_uid'] = get_uid
  >>> plugin['get_pageid'] = get_pageid
  >>> plugin['exec_js'] = exec_js
  >>> from src.imports import graphics as g


.. _`init()`:

Testing init()
---------------

Let us try with the default values.

    >>> g.init()
    pageid
    var divCanvas = ("div_uid");
     var newCanvas = document.createElement("canvas");
     newCanvas.setAttribute('id', 'canvas_uid');
     divCanvas.appendChild(newCanvas);
    <BLANKLINE>
    pageid
    ("canvas_uid").width=400;
     ("canvas_uid").height=400;
     ("canvas_uid").style.display = "block";
     ("canvas_uid")('2d').clearRect(0, 0, 400, 400);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeStyle = 'red';
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').fillStyle = 'white';
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').fillRect(0, 0, 400, 400);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeRect(0, 0, 400, 400);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeStyle = 'black';
    <BLANKLINE>

We'll try later with some other values, when switching to having the
origin at the bottom left corner (mathematical convention instead
of programming convention).

.. _`clear()`:

Testing clear()
---------------

    >>> g.clear()
    pageid
    ("canvas_uid").width=0;
     ("canvas_uid").height=0;
     ("canvas_uid").style.display = "block";
     ("canvas_uid")('2d').clearRect(0, 0, 0, 0);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeStyle = 'red';
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').fillStyle = 'white';
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').fillRect(0, 0, 0, 0);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeRect(0, 0, 0, 0);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeStyle = 'black';
    <BLANKLINE>

.. _`set_line_color()`:

Testing set_line_color()
------------------------

    >>> g.set_line_color('blue')
    pageid
    ("canvas_uid")('2d').strokeStyle = 'blue';
    <BLANKLINE>

.. _`set_line_colour()`:

Testing set_line_colour()
--------------------------

Same function as above, but with different spelling.

    >>> g.set_line_colour('#abcdef')
    pageid
    ("canvas_uid")('2d').strokeStyle = '#abcdef';
    <BLANKLINE>

.. _`set_fill_color()`:

Testing set_fill_color()
------------------------

    >>> g.set_fill_color('rgb(0, 1, 2)')
    pageid
    ("canvas_uid")('2d').fillStyle = 'rgb(0, 1, 2)';
    <BLANKLINE>

.. _`set_fill_colour()`:

Testing set_fill_colour()
--------------------------

Same function as above, but with different spelling.

    >>> g.set_fill_colour('rgba(0, 1, 2, 0.5)')
    pageid
    ("canvas_uid")('2d').fillStyle = 'rgba(0, 1, 2, 0.5)';
    <BLANKLINE>

.. _`line()`:

Testing line()
---------------

    >>> g.line( (1, 2), (3, 4))
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(1, 2);
     ("canvas_uid")('2d').lineTo(3, 4);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`_circle()`:

Testing \_circle()
------------------

    >>> g.circle((100, 800), 50)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').arc(100, 800, 50, 0, Math.PI*2, true);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`circle()`:

Testing circle()
-----------------

    >>> g.circle((70, 20), 10)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').arc(70, 20, 10, 0, Math.PI*2, true);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`filled_circle()`:

Testing filled_circle()
------------------------

    >>> g.filled_circle((50, 60), 40)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').arc(50, 60, 40, 0, Math.PI*2, true);
     ("canvas_uid")('2d').fill();
    <BLANKLINE>

.. _`_rectangle()`:

Testing \_rectangle()
----------------------

    >>> g.rectangle((100, 800), 50, 10)
    pageid
    ("canvas_uid")('2d').strokeRect(100, 800, 50, 10);
    <BLANKLINE>

.. _`rectangle()`:

Testing rectangle()
---------------------

    >>> g.rectangle((70, 20), 10, 30)
    pageid
    ("canvas_uid")('2d').strokeRect(70, 20, 10, 30);
    <BLANKLINE>

.. _`filled_rectangle()`:

Testing filled_rectangle()
---------------------------

    >>> g.filled_rectangle((50, 60), 40, 25)
    pageid
    ("canvas_uid")('2d').fillRect(50, 60, 40, 25);
    <BLANKLINE>

.. _`_triangle()`:

Testing \_triangle()
----------------------

    >>> g._triangle((1, 2), (3, 4), (5, 6) )
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(1, 2);
     ("canvas_uid")('2d').lineTo(3, 4);
     ("canvas_uid")('2d').lineTo(5, 6);
     ("canvas_uid")('2d').closePath();
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`triangle()`:

Testing \_triangle()
----------------------

    >>> g.triangle((11, 21), (31, 41), (51, 61) )
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(11, 21);
     ("canvas_uid")('2d').lineTo(31, 41);
     ("canvas_uid")('2d').lineTo(51, 61);
     ("canvas_uid")('2d').closePath();
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`filled_triangle()`:

Testing filled_triangle()
--------------------------

    >>> g.filled_triangle((12, 22), (32, 42), (52, 62) )
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(12, 22);
     ("canvas_uid")('2d').lineTo(32, 42);
     ("canvas_uid")('2d').lineTo(52, 62);
     ("canvas_uid")('2d').closePath();
     ("canvas_uid")('2d').fill();
    <BLANKLINE>

.. _`point()`:

Testing point()
-----------------

    >>> g.point(10, 20)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(10, 20);
     ("canvas_uid")('2d').lineTo(11, 21);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>    

.. _`validate_colour()`:

Testing validate_colour()
--------------------------

    >>> g.validate_colour('AnyAlphaString')
    True
    >>> g.validate_colour('bad string')
    False
    >>> g.validate_colour('bad_string')
    False
    >>> g.validate_colour('#abcdef')
    True
    >>> g.validate_colour('#A1B2C0')
    True
    >>> g.validate_colour('#H12345')  # H not allowed
    False
    >>> g.validate_colour('#aaa')   # too short
    False
    >>> g.validate_colour('rgb(0, 1, 255)')
    True
    >>> g.validate_colour('rgb(0, 1, 256)')  # rgb between 0 and 255
    False
    >>> g.validate_colour('rgb(0, -1, 255)')  # rgb between 0 and 255
    False
    >>> g.validate_colour('rgb(0.5, 1, 255)')  # rgb must be integers
    False
    >>> g.validate_colour('rgba(0, 1, 255, 0)')
    True
    >>> g.validate_colour('rgba(0, 1, 255, 1)')
    True
    >>> g.validate_colour('rgba(0, 1, 255, 0.5)')
    True
    >>> g.validate_colour('rgba(0, 1, 255, 1.1)')  # alpha between 0 and 1.
    False
    >>> g.validate_colour('rgba(0, 1, 255, -0.1)')  # alpha between 0 and 1.
    False
    >>> g.validate_colour('rgba(0, 1, 256, 0)')  # rbg between 0 and 255
    False


.. _`init(origin at bottom)`:

Testing init(origin at bottom)
--------------------------------

Let us try with the default values.

    >>> g.init(200, 300, border_color='green', origin='bottom')
    pageid
    ("canvas_uid").width=200;
     ("canvas_uid").height=300;
     ("canvas_uid").style.display = "block";
     ("canvas_uid")('2d').clearRect(0, 0, 200, 300);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeStyle = 'green';
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').fillStyle = 'white';
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').fillRect(0, 0, 200, 300);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeRect(0, 0, 200, 300);
    <BLANKLINE>
    pageid
    ("canvas_uid")('2d').strokeStyle = 'black';
    <BLANKLINE>


.. _`line(origin at bottom)`:

Testing line(origin at bottom)
--------------------------------

    >>> g.line( (1, 2), (3, 4))
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(1, 298);
     ("canvas_uid")('2d').lineTo(3, 296);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`_circle(origin at bottom)`:

Testing \_circle(origin at bottom)
-----------------------------------

    >>> g.circle((100, 800), 50)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').arc(100, -500, 50, 0, Math.PI*2, true);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`circle(origin at bottom)`:

Testing circle(origin at bottom)
----------------------------------

    >>> g.circle((70, 20), 10)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').arc(70, 280, 10, 0, Math.PI*2, true);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`filled_circle(origin at bottom)`:

Testing filled_circle(origin at bottom)
-----------------------------------------

    >>> g.filled_circle((50, 60), 40)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').arc(50, 240, 40, 0, Math.PI*2, true);
     ("canvas_uid")('2d').fill();
    <BLANKLINE>

.. _`_rectangle(origin at bottom)`:

Testing \_rectangle(origin at bottom)
---------------------------------------

    >>> g.rectangle((100, 800), 50, 10)
    pageid
    ("canvas_uid")('2d').strokeRect(100, -510, 50, 10);
    <BLANKLINE>

.. _`rectangle(origin at bottom)`:

Testing rectangle(origin at bottom)
--------------------------------------

    >>> g.rectangle((70, 20), 10, 30)
    pageid
    ("canvas_uid")('2d').strokeRect(70, 250, 10, 30);
    <BLANKLINE>

.. _`filled_rectangle(origin at bottom)`:

Testing filled_rectangle(origin at bottom)
--------------------------------------------

    >>> g.filled_rectangle((50, 60), 40, 25)
    pageid
    ("canvas_uid")('2d').fillRect(50, 215, 40, 25);
    <BLANKLINE>

.. _`_triangle(origin at bottom)`:

Testing \_triangle(origin at bottom)
---------------------------------------

    >>> g._triangle((1, 2), (3, 4), (5, 6) )
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(1, 298);
     ("canvas_uid")('2d').lineTo(3, 296);
     ("canvas_uid")('2d').lineTo(5, 294);
     ("canvas_uid")('2d').closePath();
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`triangle(origin at bottom)`:

Testing \_triangle(origin at bottom)
---------------------------------------

    >>> g.triangle((11, 21), (31, 41), (51, 61) )
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(11, 279);
     ("canvas_uid")('2d').lineTo(31, 259);
     ("canvas_uid")('2d').lineTo(51, 239);
     ("canvas_uid")('2d').closePath();
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>

.. _`filled_triangle(origin at bottom)`:

Testing filled_triangle(origin at bottom)
-------------------------------------------

    >>> g.filled_triangle((12, 22), (32, 42), (52, 62) )
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(12, 278);
     ("canvas_uid")('2d').lineTo(32, 258);
     ("canvas_uid")('2d').lineTo(52, 238);
     ("canvas_uid")('2d').closePath();
     ("canvas_uid")('2d').fill();
    <BLANKLINE>

.. _`point(origin at bottom)`:

Testing point(origin at bottom)
----------------------------------

    >>> g.point(10, 20)
    pageid
    ("canvas_uid")('2d').beginPath();
     ("canvas_uid")('2d').moveTo(10, 280);
     ("canvas_uid")('2d').lineTo(11, 281);
     ("canvas_uid")('2d').stroke();
    <BLANKLINE>
 










