===================
Welcome To Crunchy
===================

New: the `rst_edit widget </docs/experimental/rst_edit.html>`__ can
also be found in the experimental section of the menu



What is needed to run Crunchy?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since you are reading this, chances are that you are already using
Crunchy. If that is not the case, in addition to Crunchy you will also
need:


+ `Python <www.python.org>`__. I do mean Guido van Rossum's Python,
  not Monty Python nor a real life snake. Chances are it is already
  installed on your computer; but you do need a version no older than
  version 2.4. Crunchy has been tested with Python 2.4, 2.5, 2.6, and
  3.1 !!
+ Alternatively, you may try `Jython <www.jython.org>`__. Crunchy has
  been tested successfully with Jython 2.5.0.
+ `Firefox <firefox.com>`__. Crunchy may work (at least partially)
  with some other browsers, but it is currently only tested with
  Firefox.




Warning: mixed behaviour when working with unicode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Internally, Crunchy works with utf-8 encoding. This leads to a slight
change when using Python 2.x with Crunchy for unicode strings. For
example, when working from the terminal, on a Mac OS, the following
happens:

.. sourcecode:: python


    >>> print 'André'
    André
    >>> 'André'
    'Andr\xc3\xa9'
    >>> u'André'
    u'Andr\xe9'
    >>> print u'André'
    André


However, if you use Crunchy (with Python ... not Jython), this is what
you will see instead:

.. sourcecode:: python


    >>> print 'André'
    André
    >>> 'André'
    'Andr\xc3\xa9'
    >>> u'André'   # This is different
    u'Andr\xc3\xa9'
    >>> print u'André'   # and so is this
       Crunchy Error in trying to decode inside cometIO.py
       The likely cause is trying to print a unicode string prefixed by u
       as in u"...". If not, please file a bug report.
    AndrÃ©


If you use Jython with unicode strings, it seems that no matter what
you try, a traceback results.

When you are writing code from within Crunchy (not to be saved in a
file), and using Python 2.x, just drop the u prefix for unicode
strings and everything will work just as though you had included it
while coding in other environments.


New to Crunchy?
~~~~~~~~~~~~~~~

If you are new to Crunchy, or have used an older version, we strongly
suggest that you first go through the basic tutorial.

You can use the Crunchy Menu at the top right to come back to this
page or if you have administrator privileges, to quit Crunchy
altogether.

Note that, whenever you see this image: , it is because the Crunchy
developers (or perhaps some other tutorial writer) have written some
useful tip that you can view by clicking on them. Note that if you
click on them a second time, the useful tip will disappear. If you
don't want these images, and the information they refer to, to appear
at all, use the selector below to turn them off (except for this
page!)
irrelevant text
Other images, such as may also be used in this fashion - however,
these can not be turned off.

Other user preferences can be selected `via this link
</docs/basic_tutorial/preferences.html>`__, or via the "Preferences"
Crunchy menu item at the top-right corner.
