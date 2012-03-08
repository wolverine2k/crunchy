~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An almost typical introduction to Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I will not begin this introduction to Python the standard way, like it
is done with all other languages, by asking you to write the
traditional

.. sourcecode:: python


    print "Hello World!"


No, this would just be too boring and neither worthy of Python nor of
Crunchy. Instead, I suggest that you type the following code in the
interpreter prompt that appears just below it.

.. sourcecode:: python

    >>> answer = 211 // 5
    >>> print(answer)


If you haven't made any mistake, Python will respond with `The
Answer to The Ultimate Question Of Life, the Universe and Everything
<http://en.wikipedia.org/wiki/Image:Answer_to_Life.png>`__, at least
according to the Hitchhiker's Guide to the Galaxy. The Python
interpreter you just used was actually inspired by and adapted from
some great work by Robert Brewer. You may have also noticed that the
Python code was displayed in colour, quite unlike the boring all black
stuff of the original html page.

Impressive, isn't it? Now try the following in this other interpreter.

.. sourcecode:: python

    >>> print(answer)

Yes, WE ARE THE BORG . Crunchy's Borg interpreters all share the same
state so that variables entered in one of them are known to all the
other interpreters on the same page. However, if you are in search of
a bit of individuality, you can try the same experiment again below.


.. sourcecode:: python

    >>> print(answer)

Different prompt
````````````````

Notice how the prompt of the isolated interpreter ( `-->`) is
different from the standard Python prompt, used for the Borg
interpreter. The single `>` sign is meant as a reminder that this is
an individual interpreter.

Python/Crunchy gave you an error message, as it did not know the
answer to the ultimate question. Generally, you should only see Borg
type interpreters used in Crunchy. However, you should keep in mind
that there are other possibilities.

After seeing these amazing feats, I am convinced that you will want to
purchase Crunchy!
I'm not interested in your sales! I have to protect the general
public!
From the Monty Python Crunchy Frog sketch.
Crunchy is not for sale: it is free software. However, it is not
designed for the "general public". Using a Python interpreter on a
computer can lead to unwanted results, depending on the code that is
being executed. [ `import os:` use with caution!] We can not be held
responsible for any negative consequence of code you type in for
Crunchy/Python to execute.

More than just the basics
~~~~~~~~~~~~~~~~~~~~~~~~~

You can type in more than one line of code and interact with the
interpreter in various ways. In the examples below, I have tried to
show both what you should type in, and a preview of the response from
Crunchy. For some of these examples you may notice that, at some
point, a pop-up "help window" will appear at the top right. You can
make it go away by clicking on theX or simply keep on typing until it
goes away on its own (in most cases).

First, we start with an interaction where the interpreter will be
waiting for a response to a question.

.. sourcecode:: python

    >>> name = raw_input("What is your name? ")  # Python 2.x
    >>> name = input("What is your name? ")      # Python 3.x
    What is your name?
    [Type in your name in the input box with no prompt in front]
    >>> print(name)
    Your_name_should_appear_here


Next we show examples of loops; make sure you indent the code
properly.

.. sourcecode:: python

    >>> for i in range(4):
    ...     print(i)
    ...
    0
    1
    2
    3

We then move to various ways to access Python's help system.

.. sourcecode:: python

    >>> import sys
    >>> help(sys)   # click on the X when you're finished reading
    >>> sys?        # shortcut for help.
    >>> sys.exit?


Finally, you can view the variables defined so far (I won't show you
the expected output since it depends on what *you* tried before) using
the `dir()` function, and remove them all, effectively starting a new
session, using the `restart()` function.

.. sourcecode:: python


    >>> dir()
    >>> restart()  # specific to Crunchy
    >>> dir()


You now know enough to use the interpreter to learn about Python
following a "real" Python tutorial. You could do this at this point by
going to`the official Python tutorial
<http://docs.python.org/tut/tut.html>`__ on the python.org site.
However, I strongly suggest that you continue to learn about Crunchy
by clicking on the editor link on the left. WARNING: if you click on
the link to the official Python tutorial, you will not, in fact, be
able to try out the Python code. This is because Crunchy does not
allow interactions with unknown sites; it will simply style the page
in its own way and display it. You will need to explicitly tell it
(there are at least 3 different ways of doing this) that you consider
the site "safe" for browsing. If you really can't wait, just enter

.. sourcecode:: python


    >>> crunchy.add_site()
    >>> # docs.python.org is the answer to the first question
    >>> # trusted is the likely answer to the second


In general, you might want to be a bit cautious as to the value you
choose for the security level of a remote site. However, it's most
likely safe to write `trusted` for the security level of the
docs.python.org site.



Just a little more about the interpreter ...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Crunchy's interpreter has a few extra features that can be very useful
... but potentially tricky. Consider the following.

.. sourcecode:: python


    >>> name = "Guido van Rossum"
    >>> print(name)
    Guido van Rossum


Instead of having only two lines of text, imagine we had 20 lines. To
reproduce this example would require lots of typing. Using some
advanced feature of Crunchy, you can save yourself a fair bit of
typing. Here is how: click on the image to the right of the
interpreter. You should see appearing below it a larger box (an html
textarea for those interested) a button at the bottom. Clicking on
that button feeds the code to the interpreter. Try it out!

While this is a neat trick, there are a couple of caveats: Crunchy
takes each line as though you had typed it yourself, one line at a
time, in an interactive session.


Caveat #1
`````````

Try to click on the image, uncomment the appropriate line of code and,
if using Python 2.x, delete the next one; then click on the execute
execute button with the following.

.. sourcecode:: python


    >>> #name = raw_input("Enter your name: ") # Python 2.x
    >>> #name = input("Enter your name: ")     # Python 3.x
    >>> print "YOUR NAME IS", name


Now, try the next example below to see more clearly what happened:

.. sourcecode:: python


    >>> name


As you should see, Crunchy had taken the second line as your answer to
the first. This is unlikely to be what you want.

**First lesson:** do not use `input()` or `raw_input()` inside a box
obtained by clicking on the editor image next to an interpreter.



Caveat #2
`````````

Try again with the following example: click on the editor image and
execute the code. You will find that the interpreter will not be able
to handle the result and give you a number of error messages. When
that happens, continue reading below.

.. sourcecode:: python


    >>> def flatten(seq):
    ...     """flatten(sequence) -> list
    ...
    ...     Returns a single, flat list which contains all elements retrieved
    ...     from the sequence and all recursively contained sub-sequences
    ...     (iterables).
    ...
    ...     Examples:
    ...     >>> flatten([[[1,2,3]], [4,5], [6], 7, (8,9,10)])
    ...     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ...     """
    ...
    ...     result = []
    ...     for elem in seq:
    ...         if hasattr(elem, "__iter__") and not isinstance(elem, basestring):
    ...             result.extend(flatten(elem))
    ...         else:
    ...             result.append(elem)
    ...     return result
    ...
    >>> flatten([[[1,2,3]], [4,5], [6], 7, (8,9,10)])


The problem is due to the empty line (12). Imagine that you were
typing in the code yourself, line by line. When you enter an empty
line, the interpreter interprets this as the end of a function
definition (or a loop, or if statement, etc.). To avoid this problem,
we need to have something with no empty lines; so try again, this time
removing the empty line before executing the code.

**Second lesson:** beware of empty lines inside a box obtained by
clicking on the editor image next to an interpreter.


Advanced stuff, mostly for tutorial writers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to instruct Crunchy to insert an interpreter below a Python
code sample, one uses the `title` attribute as follows:

`<pre title="<<interpreter>> [linenumber [=starting_number]]">`
> <code>Some Python code< code>
> <code title="html">< pre>

where the square brackets indicate optional arguments, and
`<<interpreter>>` can be any value taken from the following list,
which includes some advanced options not covered in this basic
tutorial: `[interpreter, isolated, parrot, Parrots, TypeInfoConsole]`;
the standard choice should be `interpreter` (or the equivalent
`Borg`). There is also another option, `python_tutorial` which only
inserts an interpreter if there are prompts appearing in the code
sample; otherwise, it simply styles the code. For the curious, there
is yet another value that is undocumented - use the source...

Any number of interpreter "prompts" can appear within a page; if
`interpreter` has been selected, every such interpreter used **on the
same page** shares the same environment; if `isolated` is chosen, then
each such interpreter will have its own environment. Sharing the same
environment means that, if you need to import a given module as you go
through a tutorial, you only have to do it once; similarly, a variable
defined in one such interpreter will be known to others, until the
user clicks on a link to load a new page.

Any text between the `pre` tags is placed before the interpreter, in a
`pre` element and styled according to the user's preferences. If the
`linenumber` option is present, a line number will appear before each
line of input code; the line numbering will start at 1 unless a
different starting value is given.
