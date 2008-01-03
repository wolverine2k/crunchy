Boring Work
===========

This document currently has three main sections:

 - Reducing dependencies & Testing
 - Design philosophy
 - Future work

The only relevant section is the first one; the other two should be moved into a
separate document.

Reducing dependencies & Testing
-------------------------------

In order to reduce the interdependencies between the modules, and allow isolated testing
as much as possible, we use a module named interface.py which is normally initialized by
crunchy but can be initialized with mock values by a user.

This document is meant to keep track of all modules and their dependencies and
of the available unit tests.

All modules should be unit tested; we preferably use doctest-based unit tests that can be
used as supplementary documentation.

Crunchy includes a number of doctest based (.rst files) unit files which it can style 
and display, using the default crunchy.no_markup option.  (We suggest to use "python_code"
as that option when viewing these files).  These tests can be run via

- python all_tests.py, if using a Python version less than 3.0
- python all_tests_py3k.py, if using a Python version 3.x

In terms of test coverage, this is just a first draft which needs to be verified.

As a rule, every plugin should import the interface module - and
nothing else other than other plugins (and, perhaps, utilities.py) and/or modules from the Python standard library. 

In the following, we indicate which modules that are imported, with the exclusion of
modules from the standard library.

Crunchy Python files listing::

    all_tests.py
    all_tests_py3k.py
    crunchy.py
        -> import: interface, http_serve, pluginloader
    sanitize.py
        -> import: configuration, security, interface, element_tree
    src:
        cometIO.py
            -> import: configuration, interpreter, interface, utilities
        configuration.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
            -> import: interface
        CrunchyPlugin.py
            -> import: cometIO, PluginServices, interface, vlam
        errors.py
            -> import: configuration, translation
        http_serve.py
            -> import: CrunchyPlugin, interface
        interface.py # tests :2.4, 2.5, 3.0a1, 3.0a2
            -> import: tools_2k, tools_3k,  my_htmlentitydefs, translation, ElementTree++
        interpreter.py
            -> import: interface, utilities, configuration, errors
        my_htmlentitydefs.py
            -> import: None
        pluginloader.py   # partial tests: 2.4, 2.5, 3.0a1, 3.0a2
            -> import: interface
        PluginServices.py # empty file by design - no need to test.
            -> import: None
        security.py
            -> import: interface
        tools_2k.py
            -> import: errors
        tools_3k.py
            -> import: None
        translation.py
            -> import: interface
        utilities.py # tests :2.4, 2.5, 3.0a1, 3.0a2
            -> import: interface
        vlam.py
            -> import: security, interface, ElementSoup, cometIO, configuration, utilities
               
    src/plugins:
            colourize.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface, utilities
                   provides = set(["style_pycode"])
            comet.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface, cometIO
                   provides = set(["/comet", "/input"])
                ### cometIO dependency unavoidable - the entire purpose of this plugin was
                ### to include the services provided by cometIO ["/comet", "/input"]
                ### in the plugin directory so that it was easier to find.
            editarea.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface
                   provides = set(["editarea"])
                   requires = set(["/save_file", "/load_file"])
            execution.py
                -> import: interface
                   provides = set(["/exec"])
            file_service.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface, configuration
                   provides = set(["/save_file", "/load_file", "/save_and_run", "/run_external"])
                ### configuration dependency unavoidable; file_service can be used to set
                ### a variable in configuration.py
            handle_default.py
                -> import: interface
            handle_local.py
                -> import: interface
                   provides = set(["/local", "/generated_image"])
            handle_remote.py
                -> import: interface
                   provides = set(["/remote"])
            io_widget.py
                -> import: interface, editarea
                   provides = set(["io_widget"])
            links.py
                -> import: interface
            menu.py
                -> import: interface, security
                ### security dependency unavoidable; used to scan non-standard menus for
                ### security holes.
            rst.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface
                   provides = set(["/rst"])
            security_advisor.py
                -> import: interface
                   provides = set(["/allow_site", "/enter_key", "/set_trusted", "/remove_all"])
            tooltip.py
                -> import: interface, interpreter
                   provides = set(["/dir","/doc"])
                ### interpreter dependency unavoidable - need to initialize a Borg console
                ### if the shared information is to be made available in the tooltip.
            vlam_doctest.py
                -> import: interface, utilities
                   requires =  set(["editor_widget", "io_widget"])
            vlam_editor.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface, utilities
                   provides = set(["editor_widget"])
                   requires = set(["io_widget", "/exec", "/run_external", "style_pycode",
                                   "editarea"])
            vlam_image_file.py
                -> import: interface
                   provides = set(["image_file_widget"])
                   requires = set(["io_widget", "/exec", "style_pycode",  "editor_widget"])
            vlam_interpreter.py
                -> import: interface, utilities, colourize
                   requires = set(["io_widget", "/exec"])
            vlam_load_local.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface
                   requires = set(["/local"])
            vlam_load_remote.py # tests :2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface
                   requires = set(["/remote"])

    src/imports:
            c_turtle.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: None
            graphics.py
                -> import: interface
            math_graphics.py
                -> import: interface
            turtle_js.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
                -> import: interface, c_turtle
            turtle_tk.py  # empty file for now...

The following are not likely to be tested by us::
            
    src/element_tree:
            BeautifulSoup.py
                -> import: None
            ElementPath.py
                -> import: None
            ElementSoup.py
                -> import: BeautifulSoup, ElementTree
            ElementTree.py
                -> import: ElementPath
            HTMLTreeBuilder.py
                -> import: ElementTree


The following are the actual links to existing test files.

#. test_c_turtle.rst_
#. test_colourize.rst_
#. test_comet.rst_
#. test_configuration.rst_
#. test_editarea.rst_
#. test_file_service.rst_
#. test_pluginloader.rst_
#. test_rst.rst_
#. test_turtle_js.rst_
#. test_interface.rst_
#. test_utilities.rst_
#. test_vlam_editor.rst_
#. test_vlam_load_local.rst_
#. test_vlam_load_remote.rst_

.. _test_c_turtle.rst: test_c_turtle.rst
.. _test_colourize.rst: test_colourize.rst
.. _test_comet.rst: test_comet.rst
.. _test_configuration.rst: test_configuration.rst
.. _test_editarea.rst: test_editarea.rst
.. _test_file_service.rst: test_file_service.rst
.. _test_pluginloader.rst: test_pluginloader.rst
.. _test_turtle_js.rst: test_turtle_js.rst
.. _test_interface.rst: test_interface.rst
.. _test_rst.rst: test_rst.rst
.. _test_utilities.rst: test_utilities.rst
.. _test_vlam_editor.rst: test_vlam_editor.rst
.. _test_vlam_load_local.rst: test_vlam_load_local.rst
.. _test_vlam_load_remote.rst: test_vlam_load_remote.rst

Design philosophy
-----------------

Talk about the design philosophy from the point of view of 

 - an end user
 - a tutorial writer
 - a developer
 

Future work
-----------

Whereas we should use the main site (code.google.com) and the "issues" as a repository for
desired features, this section can be used as a quick off-line reminder.

  - it should be possible to switch a debug flag for a given module dynamically while Crunchy
    is running.
  - debug "print" statements should be made more robust (like they are in cometIO.py); currently
    they can be interfered with apparently by changes to sys.stdout that occur while Crunchy
    is running.