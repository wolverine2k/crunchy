colourize.py tests
==================

Note that in order to have tests compatible with Python 2.x and 3.x, we can not use "print"
since it is a statement in 2.x and a function in 3.x; the same is true with "exec".
Furthermore, parsing of code sample with comments appears to be done differently by the tokenizer;
we need to be a little bit more careful about those.

Since some behaviour differ between Python versions, we will have to make some adjustments,
using the ELLIPSIS directive to skip over differences for print/exec and comments as noted above.

Introduction
------------

This file contains tests of styling Python code.  Unfortunately, the
additional markup makes it near impossible to have short (<80 characters)
output lines.

We start by initializing a Colourizer instance, after we do the usual
dance and clear any remaining entries in the plugin and config dicts.

    >>> from src.interface import plugin, config, get_base_dir
    >>> plugin.clear()
    >>> config.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()
    >>> import src.plugins.colourize as colourize
    >>> styler = colourize.Colourizer()

We now style a few code samples.  First, some straight Python code.

    >>> code_sample1 = """a = 'Hello world!'
    ... for i in range(3):
    ...     a += str(i)
    ... class test_case(object):
    ...     def __init__(self):
    ...         pass
    ... """
    >>> styled_code1 = styler.parseListing(code_sample1)
    >>> print(styled_code1)
    <span class='py_variable'>a</span><span class='py_op'> =</span><span class='py_string'> 'Hello world!'</span>
    <span class='py_keyword'>for</span><span class='py_variable'> i</span><span class='py_keyword'> in</span><span class='py_builtins'> range</span><span class='py_op'>(</span><span class='py_number'>3</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span>    </span><span class='py_variable'>a</span><span class='py_op'> +=</span><span class='py_builtins'> str</span><span class='py_op'>(</span><span class='py_variable'>i</span><span class='py_op'>)</span>
    <span class='py_keyword'>class</span><span class='py_variable'> test_case</span><span class='py_op'>(</span><span class='py_builtins'>object</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span>    </span><span class='py_keyword'>def</span><span class='py_special'> __init__</span><span class='py_op'>(</span><span class='py_variable'>self</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span>        </span><span class='py_keyword'>pass</span>
    <BLANKLINE>

We know that the generated work does the required processing as we have
done some functional testing and looked at similar code displayed by
a browser.  We will use such code samples from now on, assuming them
to be correct, as we develop additional functionality.

Next, another code sample but with added comments; since comment parsing differ slightly
between Python 2.x and 3.x, we will keep the example reasonably short.
Note that we also removed the last empty line.

    >>> code_sample2 = """#First comment
    ... a = 'Hello world!'"""

[[ Note that we need to re-initialize the Colourizer as a new instance.
This was not needed for Crunchy version prior 0.8.2 as we used to call
a reset() method after each styling (which is redundant with the new
version that does not call Colourizer directly). ]]


    >>> styler = colourize.Colourizer()
    >>> styled_code2 = styler.parseListing(code_sample2)
    >>> print(styled_code2) #doctest:+ELLIPSIS
    <span class='py_comment'>#First comment...
    ...<span class='py_variable'>a</span><span class='py_op'> =</span><span class='py_string'> 'Hello world!'</span>

Note how the comments result in a </span> inserted at the beginning of the
next line.  This requires special consideration when styling code with
interpreter prompts.

Next, we redo the same tests, but this time with added line numbers.
    >>> styler = colourize.Colourizer(offset=0)
    >>> styled_code1a = styler.parseListing(code_sample1)
    >>> print(styled_code1a)
    <span class='py_linenumber'>  1 </span><span class='py_variable'>a</span><span class='py_op'> =</span><span class='py_string'> 'Hello world!'</span>
    <span class='py_linenumber'>  2 </span><span class='py_keyword'>for</span><span class='py_variable'> i</span><span class='py_keyword'> in</span><span class='py_builtins'> range</span><span class='py_op'>(</span><span class='py_number'>3</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span class='py_linenumber'>  3 </span><span>    </span><span class='py_variable'>a</span><span class='py_op'> +=</span><span class='py_builtins'> str</span><span class='py_op'>(</span><span class='py_variable'>i</span><span class='py_op'>)</span>
    <span class='py_linenumber'>  4 </span><span class='py_keyword'>class</span><span class='py_variable'> test_case</span><span class='py_op'>(</span><span class='py_builtins'>object</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span class='py_linenumber'>  5 </span><span>    </span><span class='py_keyword'>def</span><span class='py_special'> __init__</span><span class='py_op'>(</span><span class='py_variable'>self</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span class='py_linenumber'>  6 </span><span>        </span><span class='py_keyword'>pass</span>
    <span class='py_linenumber'>  7 </span>


    >>> styler = colourize.Colourizer(offset=0)
    >>> styled_code2a = styler.parseListing(code_sample2)
    >>> print(styled_code2a)  #doctest:+ELLIPSIS
    <span class='py_linenumber'>  1 </span><span class='py_comment'>#First comment...
    ...<span class='py_linenumber'>  2 </span><span class='py_variable'>a</span><span class='py_op'> =</span><span class='py_string'> 'Hello world!'</span>


Note again how the comments ending one line result in a </span> inserted at the beginning of the
next one.

A final example that starts at line 11 (offset of 10)
    >>> styler = colourize.Colourizer(offset=10)
    >>> styled_code2b = styler.parseListing(code_sample2)
    >>> print(styled_code2b)  #doctest:+ELLIPSIS
    <span class='py_linenumber'> 11 </span><span class='py_comment'>#First comment...
    ...<span class='py_linenumber'> 12 </span><span class='py_variable'>a</span><span class='py_op'> =</span><span class='py_string'> 'Hello world!'</span>



New stuff
---------

We use TDD to change colourize.py.
First, we define a new function that will be called, instead of calling an
instance of the Colourizer class directly.
UPDATE: this function also strips empty lines; so to compare with the
previous cases, we may need to add an extra line "\n" by hand.

    >>> print(styled_code1 == colourize._style(code_sample1)[1] + "\n")
    True

After adding a line numbering option, we can reproduce a second example.
(note: we cannot simply use the example with blankline for comparison;
however, this does not mean that the code does not work as intended in this case,
just that we deal with empty lines differently with the style() function as
we do with the simple parseListing method)

    >>> print(styled_code2a == colourize._style(code_sample2, offset=0)[1])
    True

Extracting code from an interpreter session.
--------------------------------------------

Consider the following simulated interpreter sessions (using square brackets
and commas to represent the prompt), to be embedded in an html page.

]]] print "Hello world!"

    >>> code_sample3 = """>>> print 'Hello world!'"""
    >>> python_code3, extracted3 = colourize.extract_code_from_interpreter(code_sample3)
    >>> print(python_code3)
    print 'Hello world!'
    >>> print(extracted3)
    [('&gt;&gt;&gt; ', 1)]


]]] print "Hello world!"
Hello world!
]]] for i in range(3):
,,,     print i*i

    >>> code_sample4 = """>>> print 'Hello world!'
    ... Hello world!
    ... >>> for i in range(3):
    ... ...     print i*i"""
    >>> python_code4, extracted4 = colourize.extract_code_from_interpreter(code_sample4)
    >>> print(python_code4)
    print 'Hello world!'
    for i in range(3):
        print i*i
    >>> print(extracted4)
    [('&gt;&gt;&gt; ', 1), ('', 'Hello world!'), ('&gt;&gt;&gt; ', 2), ('... ', 3)]


We can style the code as before.
    >>> styled_code3 = colourize._style(python_code3)[1]
    >>> styled_code4 = colourize._style(python_code4)[1]

For future reference, we will document as tests here styling examples
with line numbers added of the previous two cases.

    >>> print(colourize._style(code_sample3, offset=4)[1])  #doctest:+ELLIPSIS
    <span class='py_linenumber'>  5 </span><span class="py_prompt">&gt;&gt;&gt; </span><span class='...'>print</span><span class='py_string'> 'Hello world!'</span>
    >>> print(colourize._style(code_sample4, offset=0)[1])  #doctest:+ELLIPSIS
    <span class='py_linenumber'>  1 </span><span class="py_prompt">&gt;&gt;&gt; </span><span class='...'>print</span><span class='py_string'> 'Hello world!'</span>
    <span class='py_linenumber'>    </span><span class="py_output">Hello world!</span>
    <span class='py_linenumber'>  2 </span><span class="py_prompt">&gt;&gt;&gt; </span><span class='py_keyword'>for</span><span class='py_variable'> i</span><span class='py_keyword'> in</span><span class='py_builtins'> range</span><span class='py_op'>(</span><span class='py_number'>3</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span class='py_linenumber'>  3 </span><span class="py_prompt">... </span><span>    </span><span class='...'>print</span><span class='py_variable'> i</span><span class='py_op'>*</span><span class='py_variable'>i</span>

Next, we define a function to add back the prompt and output to the
styled code from a simulated interpreter session.

    >>> fully_styled3 = colourize.add_back_prompt_and_output(styled_code3, extracted3)
    >>> print(fully_styled3)  #doctest:+ELLIPSIS
    <span class="py_prompt">&gt;&gt;&gt; </span><span class='...'>print</span><span class='py_string'> 'Hello world!'</span>
    >>> fully_styled4 = colourize.add_back_prompt_and_output(styled_code4, extracted4)
    >>> print(fully_styled4)  #doctest:+ELLIPSIS
    <span class="py_prompt">&gt;&gt;&gt; </span><span class='...'>print</span><span class='py_string'> 'Hello world!'</span>
    <span class="py_output">Hello world!</span>
    <span class="py_prompt">&gt;&gt;&gt; </span><span class='py_keyword'>for</span><span class='py_variable'> i</span><span class='py_keyword'> in</span><span class='py_builtins'> range</span><span class='py_op'>(</span><span class='py_number'>3</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span class="py_prompt">... </span><span>    </span><span class='...'>print</span><span class='py_variable'> i</span><span class='py_op'>*</span><span class='py_variable'>i</span>

By inspection, we conclude that it does appear to be correct.

In previous version, we noticed that there was a bug when a comment
was inserted as the last line of an interpreter session.  We need to
see if we have to take care of this in this version.

    >>> end_comment6 = '''>>> # this is a comment'''
    >>> python_code6, extracted6 = colourize.extract_code_from_interpreter(end_comment6)
    >>> print(colourize._style(python_code6)[1])
    <span class='py_comment'># this is a comment</span>
    >>> py6, styled6, error_found = colourize._style(end_comment6) # letting style do its thing
    >>> print(styled6)
    <span class="py_prompt">&gt;&gt;&gt; </span><span class='py_comment'># this is a comment</span>
    >>> print(py6)
    # this is a comment

This looks ok; let us try a slightly longer example.
    >>> end_comment7 = """>>> print 'Hello world!'
    ... Hello world!
    ... >>> for i in range(3):
    ... ...     print i*i
    ... >>> # another comment."""
    >>> python_code7, extracted7 = colourize.extract_code_from_interpreter(end_comment7)
    >>> print(colourize._style(python_code7)[1])  #doctest:+ELLIPSIS
    <span class='...'>print</span><span class='py_string'> 'Hello world!'</span>
    <span class='py_keyword'>for</span><span class='py_variable'> i</span><span class='py_keyword'> in</span><span class='py_builtins'> range</span><span class='py_op'>(</span><span class='py_number'>3</span><span class='py_op'>)</span><span class='py_op'>:</span>
    <span>    </span><span class='...'>print</span><span class='py_variable'> i</span><span class='py_op'>*</span><span class='py_variable'>i</span>
    <span class='py_comment'># another comment.</span>

Again, by inspection, this looks correct.

We now proceed to implement a new feature, intended to automatically detect
if a python code sample represents a simulated interpreter session.

ASSUMPTION: we will assume, as has been the case so far, that any code will
be aligned to the left i.e. that there is no extra spaces added at the
beginning of each line (unlike the doctests examples embedded in this page).
In the future, if it proves necessary, this condition could be relaxed,
at the cost of some minor increase complexity of the code written so far.

We consider the two simplest case first.
    >>> sample1 = '''print "Hello world!"'''
    >>> sample2 = '''>>> print "Hello world!"'''
    >>> print(colourize.is_interpreter_session(sample1))
    False
    >>> print(colourize.is_interpreter_session(sample2))
    True

We then consider two more cases, with blank lines inserted at the beginning:
    >>> sample7 = '''\n\nprint "Hello world!"'''
    >>> sample8 = '''   \n  \n>>> print "Hello world!"'''
    >>> print(colourize.is_interpreter_session(sample7))
    False
    >>> print(colourize.is_interpreter_session(sample8))
    True

We use this function inside colourize.py to proceed, reusing some
examples introduced previously.  We know, from the tests done above,
that the new version still works with non-interpreter code.  We can use
some previous examples to test the interpreter version.

    >>> print(colourize._style(code_sample3)[1] == fully_styled3)
    True
    >>> print(colourize._style(code_sample4)[1] == fully_styled4)
    True

In case we find a discrepancy, we compare with the expected result.
    >>> print(colourize._style(code_sample3)[1])  #doctest:+ELLIPSIS
    <span class="py_prompt">&gt;&gt;&gt; </span><span class='...'>print</span><span class='py_string'> 'Hello world!'</span>

Using this code with sample pages, we noted that sometimes blank lines
were added either at the beginning and/or at the end of a code sample.
As this can lead to too much blank vertical spaces inserted in html pages
displayed by Crunchy, we will introduce a function which will be used to
removed such lines.

    >>> test_blank = '\n \r\n\n\r  \nline1\nline2 followed by blank line\n\nline3\n \n'
    >>> print(colourize.trim_empty_lines_from_end(test_blank))
    line1
    line2 followed by blank line
    <BLANKLINE>
    line3
    >>> test_blank2 = 'line1\nline2'
    >>> print(colourize.trim_empty_lines_from_end(test_blank2))
    line1
    line2

Testing the plugin
------------------

First, we define and test a function to extract the text content from
a piece of html code, converting <br/> into "\n"

    >>> et = colourize.et
    >>> sample = "<pre>a\nb<br/>c<span>d</span></pre>"
    >>> pre = et.fromstring(sample)
    >>> print(colourize.extract_code(pre))
    a
    b
    cd

We also have a function to extract the value of the linenumber option if present.
    >>> print(colourize.get_linenumber_offset("junk"))
    None
    >>> print(colourize.get_linenumber_offset("linenumber"))
    0
    >>> print(colourize.get_linenumber_offset("linenumber=4"))
    3
    >>> print(colourize.get_linenumber_offset("linenumber =    22"))
    21
    >>> print(colourize.get_linenumber_offset("linenumber  start =    24"))
    0
    >>> print(colourize.get_linenumber_offset("LineNumber = 3"))
    2

Next, a function to replace an ElementTree Element "in place".
    >>> original = '<a b="c">d<e>f</e>g</a>'
    >>> new = '<aa bb="cc">dd<ee>ff</ee>gg</aa>'
    >>> elem = et.fromstring(original)
    >>> replacement = et.fromstring(new)
    >>> elem_id = id(elem)
    >>> colourize.replace_element(elem, replacement)
    >>> print(elem_id == id(elem)) # same object as before
    True
    >>> print(et.tostring(elem) == new)# but with new content
    True
    >>> print(new)
    <aa bb="cc">dd<ee>ff</ee>gg</aa>
    >>> print(et.tostring(elem))
    <aa bb="cc">dd<ee>ff</ee>gg</aa>

Next, we introduce a series of tests of increasing complexity.
First, some unstyled code.

    >>> sample = '<pre>print "Hello World!"</pre>'
    >>> pre = et.fromstring(sample)
    >>> pre.attrib['title'] = 'py_code'
    >>> py_code, new_elem, dummy_error = colourize.style(pre)
    >>> styled = et.tostring(new_elem)
    >>> print(py_code)
    print "Hello World!"
    >>> print(styled) #doctest:+ELLIPSIS
    <pre class="crunchy" title="py_code">
    <span class="...">print</span><span class="py_string"> "Hello World!"</span>
    </pre>


Next, some simple styled code
    >>> sample = '<pre title="junk">print "Hello World!"</pre>'
    >>> pre = et.fromstring(sample)
    >>> py_code, new_elem, dummy_error = colourize.style(pre)
    >>> styled = et.tostring(new_elem)
    >>> print(py_code)
    print "Hello World!"
    >>> print(styled)#doctest:+ELLIPSIS
    <pre class="crunchy" title="junk">
    <span class="...">print</span><span class="py_string"> "Hello World!"</span>
    </pre>

In the following example, the order of the attributes is changed by
ElementTree - at least in the version used for this test.

    >>> sample = '<pre title="junk" tag="other">print <span>"Hello World!"</span></pre>'
    >>> pre = et.fromstring(sample)
    >>> py_code, new_elem, dummy_error = colourize.style(pre)
    >>> styled = et.tostring(new_elem)
    >>> print(py_code)
    print "Hello World!"
    >>> print(styled)#doctest:+ELLIPSIS
    <pre class="crunchy" tag="other" title="junk">
    <span class="...">print</span><span class="py_string"> "Hello World!"</span>
    </pre>

Finally, a test including the linenumber option
    >>> sample = '<pre title="junk linenumber=2">print "Hello World!"</pre>'
    >>> pre = et.fromstring(sample)
    >>> py_code, new_elem, dummy_error = colourize.style(pre)
    >>> styled = et.tostring(new_elem)
    >>> print(py_code)
    print "Hello World!"
    >>> print(styled)#doctest:+ELLIPSIS
    <pre class="crunchy" title="junk linenumber=2">
    <span class="py_linenumber">  2 </span><span class="...">print</span><span class="py_string"> "Hello World!"</span>
    </pre>

Make sure we parse properly from html tree with a prompt included.

    >>> sample = """<html><body><pre title="py_code">>>> print 'Hello!'</pre></body></html>"""
    >>> tree = et.fromstring(sample)
    >>> pre2 = tree.find(".//pre")
    >>> pycode, new_elem, dummy_error = colourize.style(pre2)
    >>> print(pycode)
    print 'Hello!'
    >>> print(et.tostring(new_elem))#doctest:+ELLIPSIS
    <pre class="crunchy" title="py_code">
    <span class="py_prompt">&gt;&gt;&gt; </span><span class="...">print</span><span class="py_string"> 'Hello!'</span>
    </pre>

Testing with a <code> element that is followed by some text; this
tests the proper handling of an Element's "tail".

    >>> sample = """<html><body><p> An embedded code sample as in
    ...            <code title="py_code">print 'Hi!'
    ...            </code> with a tail.</p></body></html>"""
    >>> tree = et.fromstring(sample)
    >>> pre2 = tree.find(".//code")
    >>> pycode, new_elem, dummy_error = colourize.style(pre2)
    >>> print(pycode)
    print 'Hi!'
    >>> print(et.tostring(new_elem))#doctest:+ELLIPSIS
    <code class="crunchy" title="py_code">
    <span class="...">print</span><span class="py_string"> 'Hi!'</span>
    </code> with a tail.
