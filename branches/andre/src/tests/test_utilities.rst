utilities.py tests
==================

Tested successfully with Python 2.4, 2.5 and 3.0a1

    >>> import src.utilities as utilities

First, testing some log id.
    >>> fake_id1 = "id"
    >>> fake_id2 = "id with space"
    >>> fake_id3 = "_id: with 8.66, _numbers123"

    >>> fake_vlam1 = "interpreter log_id=(%s)"%fake_id1
    >>> fake_vlam1a = "interpreter log_id = ( %s )"%fake_id1
    >>> fake_vlam2 = "interpreter log_id=(%s)"%fake_id2
    >>> fake_vlam2a = "interpreter log_id = ( %s )"%fake_id2
    >>> fake_vlam3 = "interpreter log_id=(%s)"%fake_id3
    >>> fake_vlam3a = "interpreter log_id = ( %s )  other = (dumb)"%fake_id3
    
Now, testing the extraction itself
    >>> print(fake_id1 == utilities.extract_log_id(fake_vlam1))
    True
    >>> print(fake_id1 == utilities.extract_log_id(fake_vlam1a))
    True
    >>> print(fake_id2 == utilities.extract_log_id(fake_vlam2))
    True
    >>> print(fake_id2 == utilities.extract_log_id(fake_vlam2a))
    True
    >>> print(fake_id3 == utilities.extract_log_id(fake_vlam3))
    True
    >>> print(fake_id3 == utilities.extract_log_id(fake_vlam3a))
    True

It's probably a good idea to check at some failing tests as well
    >>> print(fake_id2 == utilities.extract_log_id(fake_vlam1))
    False
    >>> print(utilities.extract_log_id("Move along, there is nothing here"))
    <BLANKLINE>


Testing how well empty lines are stripped from the end of code segments.
------------------------------------------------------------------------

Define test data.

    >>> strip_none = "Hello, World!"
    >>> strip_top = "\nHello, World!"
    >>> strip_bottom = "Hello, World!\n"
    >>> strip_both = "\nHello, World!\n"
    >>> strip_mixed = "\nHello,\n\nWorld!\n"
    >>> strip_with_spaces = "   \nHello World!\n \r "

Carry out tests on test data, checking that results were correct.

	>>> print(utilities.trim_empty_lines_from_end(strip_none) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_top) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_bottom) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_both) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_mixed) == "Hello,\n\nWorld!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_with_spaces) == "Hello World!")
	True
	

Testing conversion of HTML special characters
---------------------------------------------

Define tests and expected results.

	>>> html_lt_test = "Airspeed Velocity of Unladen African Swallow < Airspeed Velocity of Unladen European Swallow"
	>>> html_lt_result = "Airspeed Velocity of Unladen African Swallow &lt; Airspeed Velocity of Unladen European Swallow"
	>>> html_and_test = "Arthur & Patsy"
	>>> html_and_result = "Arthur &amp; Patsy"
	>>> html_gt_test = "Witch's Weight > Duck's Weight?"
	>>> html_gt_result = "Witch's Weight &gt; Duck's Weight?"
	>>> html_combo_test = "x < y && y > z"
	>>> html_combo_result = "x &lt; y &amp;&amp; y &gt; z"

Carry out tests
	>>> print(utilities.changeHTMLspecialCharacters(html_lt_test) == html_lt_result)
	True
	>>> print(utilities.changeHTMLspecialCharacters(html_and_test) == html_and_result)
	True
	>>> print(utilities.changeHTMLspecialCharacters(html_gt_test) == html_gt_result)
	True
	>>> print(utilities.changeHTMLspecialCharacters(html_combo_test) == html_combo_result)
	True


Testing the "sanitization" of HTML
----------------------------------

When using Py3k, BeautifulSoup is not available ... and the only parser
we can use successfully with ElementTree is an xml parser.  This means that
it does require all tags to be closed, even those that are not required by html.
So, we "sanitize" the html code by either removing such tags altogether, or
closing them if possible.

Closing <link>
    >>> in1 = "some junk <link more junk here> more <junk>"
    >>> print(utilities.close_link(in1))
    some junk <link more junk here/> more <junk>
    >>> print(utilities.sanitize_html_for_elementtree(in1))
    some junk <link more junk here/> more <junk>
   
Closing <input>
    >>> in2 = "some junk <input more junk here> more <junk>"
    >>> print(utilities.close_input(in2))
    some junk <input more junk here/> more <junk>
    >>> print(utilities.sanitize_html_for_elementtree(in2))
    some junk <input more junk here/> more <junk>

Closing <meta>
    >>> in3 = "some junk <meta more junk here> more <junk>"
    >>> print(utilities.close_meta(in3))
    some junk <meta more junk here/> more <junk>
    >>> print(utilities.sanitize_html_for_elementtree(in3))
    some junk <meta more junk here/> more <junk>

Closing <img>
    >>> in4 = "some junk <img more junk here> more <junk>"
    >>> print(utilities.close_img(in4))
    some junk <img more junk here/> more <junk>
    >>> print(utilities.sanitize_html_for_elementtree(in4))
    some junk <img more junk here/> more <junk>

Removing <script>
    >>> in5 = "junk <script> some junk </script> junk"
    >>> print(utilities.remove_script(in5))
    junk  junk
    >>> print(utilities.sanitize_html_for_elementtree(in5))
    junk  junk

    