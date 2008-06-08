Crunchy: documentation, testing, and all that.
==============================================

This document has three main sections:

 - Testing
 - The ins and outs of Crunchy plugins
 - Reducing dependencies & Testing

 
 To find out how to write tests, please read how_to.rst_
 
 .. _how_to.rst: how_to.rst

Testing
---------

All modules should be unit tested; we preferably use doctest-based unit tests that can be
used as supplementary documentation.

In addition, we have some functional testing, some of which is automated using Selenium.
This will need to be documented at a later time.

Crunchy includes a number of doctest based (.rst files) unit files which it can style 
and display, using the default crunchy.no_markup option.  (We suggest to use "python_code"
as that option when viewing these files).  These tests can be run via

- python all_tests.py

The following are the actual links to existing test files.

#. test_c_turtle.rst_
#. test_colourize.rst_
#. test_comet.rst_
#. test_configuration.rst_
#. test_dhtml.rst_
#. test_doc_code_check.rst_
#. test_editarea.rst_
#. test_execution.rst_
#. test_file_service.rst_
#. test_handle_local.rst_
#. test_handle_remote.rst_
#. test_interface.rst_
#. test_io_widget.rst_
#. test_links.rst_
#. test_pluginloader.rst_
#. test_rst.rst_
#. test_security.rst_
#. test_turtle_js.rst_
#. test_utilities.rst_
#. test_vlam_editor.rst_
#. test_vlam_load_local.rst_
#. test_vlam_load_remote.rst_

.. _test_c_turtle.rst: test_c_turtle.rst
.. _test_colourize.rst: test_colourize.rst
.. _test_comet.rst: test_comet.rst
.. _test_configuration.rst: test_configuration.rst
.. _test_dhtml.rst: test_dhtml.rst
.. _test_doc_code_check.rst: test_doc_code_check.rst
.. _test_editarea.rst: test_editarea.rst
.. _test_execution.rst: test_execution.rst
.. _test_file_service.rst: test_file_service.rst
.. _test_handle_local.rst: test_handle_local.rst
.. _test_handle_remote.rst: test_handle_remote.rst
.. _test_interface.rst: test_interface.rst
.. _test_io_widget.rst: test_io_widget.rst
.. _test_links.rst: test_links.rst
.. _test_pluginloader.rst: test_pluginloader.rst
.. _test_turtle_js.rst: test_turtle_js.rst
.. _test_rst.rst: test_rst.rst
.. _test_security.rst: test_security.rst
.. _test_utilities.rst: test_utilities.rst
.. _test_vlam_editor.rst: test_vlam_editor.rst
.. _test_vlam_load_local.rst: test_vlam_load_local.rst
.. _test_vlam_load_remote.rst: test_vlam_load_remote.rst

The ins and outs of Crunchy plugins
-----------------------------------

Crunchy has a simple plugin architecture.  To add new capabilities for Crunchy,
one can write a simple Python module and put it in the plugins directory.
Provided that module has a register() function, Crunchy will identify it
and incorporate its capabilities.

At the moment, plugins can add four different types of capabilities:

 1. Services
 2. Tag handler
 3. Http handler
 4. Extension handler

1. Services, in Crunchy terminology, are simply functions that are made
available to other parts of code (for example, to other plugins).  An
example of a "service" is the code styling service - available from
colourize.py.   It is registered via the instruction::

   plugin['register_service']("style_pycode", service_style)

2. Tag handlers, are functions which instruct what to do when Crunchy
encounters a given html tag with given attributes while processing
and html page.  For example, the module vlam_interpreter.py is a plugin
used to embed various type of Python interpreter consoles within
an html document.  An example is registered via the following::

   plugin['register_tag_handler']("pre", "title", "interpreter", insert_interpreter)
    
This gives the following instruction to Crunchy: when it parses an html document containing
the "pre" tag with attribute "title" containing the value "interpreter" such as::

   <pre title="interpreter ..."> some text </pre>

it will take that "Element" and pass it to the function insert_interpreter()
inside the vlam_interpreter.py module, and use the result as the new "Element".
It should be noted that Crunchy uses ElementTree to parse html files, transforming
documents into a series of Element [each Element corresponding to an html tag with
various pairs of attributes and values, as well as some content (text).]

3. Http handlers are instructions from the webbrowser (usually triggered via
some javascript code) that are sent back to the Crunchy server for processing.
For example, to save a Python file from the editor, the file_service.py module defines
the following http handler::

   plugin['register_http_handler']("/save_file", save_file_request_handler)

4. Extension handlers are functions that "pre-process" a file, 
based on its extension, before creating an html page for display.  
This is something that is only useful when linking to a file
of that type directly from the Crunchy tutorial with an absolute path
from the server root.  Furthermore, the file type (based on the extension)
needs to be recognized by Firefox for this to work. Still, for the sake of
completeness, we mention it here.  To register an extension, we do it as follows::

    plugin['register_preprocessor']('txt', convert_rst)

Reducing dependencies & Testing
-------------------------------

In order to reduce the interdependencies between the modules, and allow isolated testing
as much as possible, we use a module named interface.py which is normally initialized by
crunchy but can be initialized with mock values by a user.

As a rule, every plugin should import the interface module and, if possible,
nothing else other than other plugins (and, perhaps, utilities.py) 
and/or modules from the Python standard library. 

More details can be found in how_to.rst_

.. _how_to.rst: how_to.rst


