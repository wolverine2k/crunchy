editarea.py tests
==================

Tested successfully with Python 2.4, 2.5 and 3.0a1

editarea.py is a plugin whose purpose is to insert the appropriate code in 
a page to enable the javascript based editor "editarea".  It has the following functions
that require testing:

1. register(): registers a service available to other plugins.
2. enable_editarea(): enables an editarea editor on a given element (textarea) of a page.
3. add_hidden_load_and_save(): inserts the appropriate html/javascript code required to
   load and save (Python) files.
4. addLoadPython(): Inserts the two forms required to browse for and load a local Python
   file.
5. addSavePython(): Inserts the two forms required to browse for and load a local Python
   file.

Since enable_editarea() calls add_hidden_load_and_save() which, in turns, calls the
remaining two functions, we will test them in reverse, that is, the test order will be
1, 5, 4, 3, 2.

Note that the purpose of most of these functions is simply to append new html tags
with various attributes.  As a result, the tests that need to be performed are
rather simplistic and tedious.  They also have been written "after the fact" since
the real test for developing the code was in looking at the UI that was generated.

Before we proceed with testing individual functions, we need to import interface.py and
do a variable assignment.

    >>> from src.interface import config, plugin, Element
    >>> config['editarea_language'] = 'en'
    >>> plugin['session_random_id'] = '42'
    >>> service = None
    >>> def dummy_register(fn, name):
    ...     global service
    ...     service = fn
    ...
    >>> plugin['register_service'] = dummy_register

We then need to import editarea.py
    >>> import src.plugins.editarea as editarea


1. Testing register()
---------------------

   >>> editarea.register()
   >>> print(service == editarea.enable_editarea)
   True

5. Testing addSavePython():
---------------------------

We start by creating an Element which will be manipulated by the function we wish to test.
    >>> elem = Element('parent')
    >>> id_1 = 'one'
    >>> id_2 = 'two'
    >>> editarea.addSavePython(elem, id_1, id_2)

Next, as a first crude test, we investigate to see if all the required elements 
have been inserted (and none unexpected).

    >>> br = []
    >>> forms = []
    >>> inputs = []
    >>> buttons = []
    >>> parent = []
    >>> for el in elem.getiterator():
    ...     if el.tag == "br": 
    ...         br.append(el)
    ...     elif el.tag == "form":
    ...         forms.append(el)
    ...     elif el.tag == "input":
    ...         inputs.append(el)
    ...     elif el.tag == "button":
    ...         buttons.append(el)
    ...     elif el.tag == "parent":
    ...         parent.append(el)
    ...     else:
    ...         print("Unexpected element found")
    ...
    >>> len(br)
    2
    >>> len(forms)
    2
    >>> len(inputs)
    2
    >>> len(parent)
    1
    >>> len(buttons)
    3

Assuming all the above pass, we can start looking at things in a bit more detail.
The first form has one 'br' as sub-subelement whereas the second does not.

    >>> forms[0].find('br') == None
    False
    >>> forms[1].find('br') == None
    True

The first form has one 'input' as a sub-element with the following characteristics.

    >>> input1 = forms[0].find('input')
    >>> input1.attrib['type']
    'file'
    >>> filename = 'filename' + id_1   # id_1 was defined previously
    >>> input1.attrib['id'] == filename   
    True
    >>> input1.attrib['size']
    '80'
    >>> len(input1.attrib)   # ensure that we don't have any attrib unaccounted for
    3

The second form has also one 'input' as a sub-element.

    >>> input2 = forms[1].find('input')
    >>> input2.attrib['type']
    'hidden'
    >>> path = 'path' + id_1
    >>> input2.attrib['id'] == path
    True
    >>> len(input2.attrib)   # ensure that we don't have any attrib unaccounted for
    2

This second form has also 3 buttons which we have found previously.
Some explicit test for their content will need to be added.

4. Testing addLoadPython():
---------------------------

Testing addLoadPython() is very similar to testing addSavePython().
We start by creating an Element which will be manipulated by the function we wish to test,
making sure they are slightly different from those used for addSavePython() so that
we don't get a correct result by accident.

    >>> elem_load = Element('load_parent')
    >>> id__1 = 'un'
    >>> id__2 = 'deux'
    >>> editarea.addLoadPython(elem_load, id__1, id__2)
    
Next, as a first crude test, we investigate to see if all the required elements 
have been inserted (and none unexpected).

    >>> br = []
    >>> forms = []
    >>> inputs = []
    >>> buttons = []
    >>> parent = []
    >>> for el in elem_load.getiterator():
    ...     if el.tag == "br": 
    ...         br.append(el)
    ...     elif el.tag == "form":
    ...         forms.append(el)
    ...     elif el.tag == "input":
    ...         inputs.append(el)
    ...     elif el.tag == "button":
    ...         buttons.append(el)
    ...     elif el.tag == "load_parent":
    ...         parent.append(el)
    ...     else:
    ...         print("Unexpected element found")
    ...
    >>> len(br)
    2
    >>> len(forms)
    2
    >>> len(inputs)
    2
    >>> len(parent)
    1
    >>> len(buttons)
    2
    
Assuming all the above pass, we can start looking at things in a bit more detail.
The first form has one 'br' as sub-subelement whereas the second does not.

    >>> forms[0].find('br') == None
    False
    >>> forms[1].find('br') == None
    True

The first form has one 'input' as a sub-element with the following characteristics.

    >>> input1 = forms[0].find('input')
    >>> input1.attrib['type']
    'file'
    >>> filename = 'filename' + id__1   # id__1 was defined previously
    >>> input1.attrib['id'] == filename   
    True
    >>> input1.attrib['size']
    '80'
    >>> len(input1.attrib)   # ensure that we don't have any attrib unaccounted for
    3

The second form has also one 'input' as a sub-element.

    >>> input2 = forms[1].find('input')
    >>> input2.attrib['type']
    'hidden'
    >>> path = 'path' + id__1
    >>> input2.attrib['id'] == path
    True
    >>> len(input2.attrib)   # ensure that we don't have any attrib unaccounted for
    2

This second form has also 2 buttons which we have found previously.
Some explicit test for their content will need to be added.

3. Testing add_hidden_load_and_save():
--------------------------------------

This is actually a bit simpler to test than the previous two as the function is shorter.
We start by creating an Element which will be manipulated by the function we wish to test,
making sure they are slightly different from those used before so that
we don't get a correct result by accident.

    >>> new_elem = Element('dummy')
    >>> id1 = 'ONE'
    >>> editarea.add_hidden_load_and_save(new_elem, id1)
    
Next, as a first crude test, we investigate to see if all the required elements 
have been inserted (and none unexpected).

    >>> br = []
    >>> forms = []
    >>> inputs = []
    >>> buttons = []
    >>> parent = []
    >>> divs = []
    >>> for el in new_elem.getiterator():
    ...     if el.tag == "br": 
    ...         br.append(el)
    ...     elif el.tag == "form":
    ...         forms.append(el)
    ...     elif el.tag == "input":
    ...         inputs.append(el)
    ...     elif el.tag == "button":
    ...         buttons.append(el)
    ...     elif el.tag == "dummy":
    ...         parent.append(el)
    ...     elif el.tag == 'div':
    ...         divs.append(el)
    ...     else:
    ...         print("Unexpected element found")
    ...
    >>> len(br)
    4
    >>> len(forms)
    4
    >>> len(inputs)
    4
    >>> len(parent)
    1
    >>> len(buttons)
    5
    >>> len(divs)
    2

We then check for the explicit content    

    >>> hidden_load_id = 'hidden_load' + id1
    >>> hidden_save_id = 'hidden_save' + id1
    >>> divs[0].attrib['id'] == hidden_load_id
    True
    >>> divs[1].attrib['id'] == hidden_save_id
    True
    >>> divs[0].attrib['class'] == 'load_python'
    True
    >>> divs[1].attrib['class'] == 'save_python'
    True


2. enable_editarea():
---------------------

Now that we have unit test for all of the functions that are called by enable_editarea(),
it is much easier to focus on the latter.  enable_editarea() will include some css and
javascript code on a given page.  To keep this implementation independent of the rest
of the code, we need to create a "fake" (or "mock") page that has the minimum
functionality required for testing - all we need to test is if it has been
called properly.

    >>> class TestPage(object):    
    ...     def __init__(self): 
    ...         self.called_css = False
    ...         self.called_js = False
    ...         self.called_include = False
    ...         self.js_file = False
    ...         self.included = set([])
    ...     def add_include(self, dummy):
    ...         self.included.add(dummy)
    ...     def add_js_code(self, dummy):
    ...         self.called_js = True
    ...     def insert_js_file(self, dummy):
    ...         self.js_file = True
    ...     def add_css_code(self, dummy):
    ...         self.called_css = True
    ...     def includes(self, dummy):
    ...         return dummy in self.included
    ...
    >>> page = TestPage()
    >>> dummy_elem = Element('dummy')
    >>> editarea.enable_editarea(page, dummy_elem, '1')
    >>> print(page.called_css)
    True
    >>> print(page.called_js)
    True
    >>> print(page.js_file)
    True
    >>> for inc in page.included:
    ...     print(inc)
    editarea_included
    hidden_load_and_save
