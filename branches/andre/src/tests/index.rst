Boring Work
===========

This document currently has four main sections:

 - List of available unit tests
 - The ins and outs of Crunchy plugins
 - Reducing dependencies & Testing
 - Design philosophy
 
 It also contain a fifth section of lesser importance.
 - Future work

Available unit tests files
--------------------------

The following are the actual links to existing test files.

#. test_c_turtle.rst_
#. test_colourize.rst_
#. test_comet.rst_
#. test_configuration.rst_
#. test_editarea.rst_
#. test_execution.rst_
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
.. _test_execution.rst: test_execution.rst
.. _test_file_service.rst: test_file_service.rst
.. _test_pluginloader.rst: test_pluginloader.rst
.. _test_turtle_js.rst: test_turtle_js.rst
.. _test_interface.rst: test_interface.rst
.. _test_rst.rst: test_rst.rst
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

At the moment, plugins can add three different types of capabilities:
1. Services
2. Tag handler
3. Http handler.

1. Services, in Crunchy terminology, are simply functions that are made
available to other parts of code (for example, to other plugins).  An
example of a "service" is the code styling service - available from
colourize.py.   It is registered via the instruction::

   plugin['register_service'](service_style, "style_pycode")

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
nothing else other than other plugins (and, perhaps, utilities.py) 
and/or modules from the Python standard library. 

In the following, we indicate which modules that are imported, with the exclusion of
modules from the standard library.

We also indicate which "services", "tag handlers" or "http handlers" are registered by
a given plugin, and which ones are required by it.

Crunchy Python files listing::

    all_tests.py
    all_tests_py3k.py
    crunchy.py
        import: interface, http_serve, pluginloader
    sanitize.py
        import: configuration, security, interface, element_tree
    src:
        cometIO.py
            import: configuration, interpreter, interface, utilities
        configuration.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
            import: interface
        CrunchyPlugin.py
            import: cometIO, PluginServices, interface, vlam
        debug.py  # contains just a dict - no need to test anything.
            import: none
        errors.py
            import: configuration, translation
        http_serve.py
            import: CrunchyPlugin, interface
        interface.py # tests :2.4, 2.5, 3.0a1, 3.0a2
            import: tools_2k, tools_3k,  my_htmlentitydefs, translation, ElementTree++
        interpreter.py
            import: interface, utilities, configuration, errors
        my_htmlentitydefs.py
            import: None
        pluginloader.py   # partial tests: 2.4, 2.5, 3.0a1, 3.0a2
            import: interface
        PluginServices.py # empty file by design - no need to test.
            import: None
        security.py
            import: interface
        tools_2k.py
            import: errors
        tools_3k.py
            import: None
        translation.py
            import: interface
        utilities.py # tests :2.4, 2.5, 3.0a1, 3.0a2
            import: interface
        vlam.py
            import: security, interface, ElementSoup, cometIO, configuration, utilities
               
    src/plugins:
            ### Note: in the following plugins, r_id is used as a synonym for
            ### plugin['session_random_id']
            colourize.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface, utilities
                plugin['register_tag_handler']("code", "title", "py_code", plugin_style)
                plugin['register_tag_handler']("code", "title", "python_code", plugin_style)
                plugin['register_tag_handler']("pre", "title", "py_code", plugin_style)
                plugin['register_tag_handler']("pre", "title", "python_code", plugin_style)
                plugin['register_service'](service_style, "style_pycode")
                plugin['register_service'](service_style_nostrip, "style_pycode_nostrip")
            comet.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface, cometIO
                plugin['register_http_handler']("/input%s"%r_id, push_input)
                plugin['register_http_handler']("/comet", comet)
                ### cometIO dependency unavoidable - the entire purpose of this plugin was
                ### to include the services provided by cometIO {"/comet", "/input"}
                ### in the plugin directory so that it was easier to find.
            editarea.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface
                requires: {"/save_file", "/load_file"}
                plugin['register_service'](enable_editarea, "enable_editarea")
            execution.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface
                plugin['register_http_handler']("/exec%s"%r_id, exec_handler)
            file_service.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface
                plugin['register_http_handler']("/save_file", save_file_request_handler)
                plugin['register_http_handler']("/load_file", load_file_request_handler)
                plugin['register_http_handler']("/save_and_run%s"%r_id, save_and_run_request_handler)
                plugin['register_http_handler']("/run_external%s"%r_id, run_external_request_handler)
                plugin['register_http_handler']("/save_file_python_interpreter", save_file_python_interpreter_request_handler)
                plugin['register_http_handler']("/save_and_run_python_interpreter%s"%r_id, save_and_run_python_interpreter_request_handler)
                plugin['register_http_handler']("/run_external_python_interpreter%s"%r_id, run_external_python_interpreter_request_handler)
            handle_default.py
                import: interface
                plugin['register_http_handler'](None, handler)
            handle_local.py
                import: interface
                plugin['register_http_handler']("/local", local_loader)
                plugin['register_http_handler']("/generated_image", image_loader)
                plugin['register_tag_handler']("meta", "title", "python_import", add_to_path)
            handle_remote.py
                import: interface
                plugin['register_http_handler']("/remote", remote_loader)
            io_widget.py
                import: interface, editarea
                plugin['register_service'](insert_io_subwidget, "insert_io_subwidget")
            links.py
                import: interface
                plugin['register_tag_handler']("a", None, None, link_handler)
                plugin['register_tag_handler']("img", None, None, src_handler)
                plugin['register_tag_handler']("link", None, None, href_handler)
                plugin['register_tag_handler']("style", None, None, style_handler)
                plugin['register_tag_handler']("a","title", "external_link", external_link)
            menu.py
                import: interface, security
                ### security dependency unavoidable; used to scan non-standard menus for
                ### security holes.
                plugin['register_tag_handler']("meta", "name", "crunchy_menu", insert_special_menu)
                plugin['register_tag_handler']("no_tag", "menu", None, insert_default_menu)
            rst.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface
                # this plugin won't be activated if docutils is not available.
                plugin['register_http_handler']("/rst", load_rst)
                plugin['register_tag_handler']("span", "title", "load_rst", insert_load_rst)
            security_advisor.py
                import: interface
                plugin['register_tag_handler']("no_tag", "security", None, insert_security_info)
                plugin['register_http_handler']("/set_trusted", set_security_list)
                plugin['register_http_handler']("/remove_all", empty_security_list)
            tooltip.py
                import: interface, interpreter
                ### interpreter dependency unavoidable - need to initialize a Borg console
                ### if the shared information is to be made available in the tooltip.
                plugin['register_service'](insert_tooltip, "insert_tooltip")
                plugin['register_http_handler']("/dir%s"%r_id, dir_handler)
                plugin['register_http_handler']("/doc%s"%r_id, doc_handler)
            vlam_doctest.py
                import: interface, utilities
                requires:  {"editor_widget", "io_widget"}
                plugin['register_tag_handler']("pre", "title", "doctest", doctest_widget_callback)
                plugin['register_http_handler']("/doctest%s"%r_id, doctest_runner_callback)
            vlam_editor.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface, utilities
                requires: {"io_widget", "/exec", "/run_external", "style_pycode", "editarea"}
                plugin['register_tag_handler']("pre", "title", "editor", insert_editor)
                plugin['register_service'](insert_editor_subwidget, "insert_editor_subwidget")
                plugin['register_tag_handler']("pre", "title", "alternate_python_version", insert_alternate_python)
                plugin['register_tag_handler']("pre", "title", "alt_py", insert_alternate_python)
                plugin['register_tag_handler']("pre", "title", "_test_sanitize_for_ElementTree", _test_sanitize_for_ElementTree)            
            vlam_image_file.py
                import: interface
                requires: {"io_widget", "/exec", "style_pycode", "editor_widget"}
                plugin['register_tag_handler']("pre", "title", "image_file", insert_image_file)
            vlam_interpreter.py
                import: interface, utilities, colourize
                requires: {"io_widget", "/exec"}
                plugin['register_tag_handler']("pre", "title", "interpreter", insert_interpreter)
                plugin['register_tag_handler']("pre", "title", "isolated", insert_interpreter)
                plugin['register_tag_handler']("pre", "title", "Borg", insert_interpreter)
                plugin['register_tag_handler']("pre", "title", "Human", insert_interpreter)
                plugin['register_tag_handler']("pre", "title", "parrot", insert_interpreter)
                plugin['register_tag_handler']("pre", "title", "Parrots", insert_interpreter)
                plugin['register_tag_handler']("pre", "title", "TypeInfoConsole", insert_interpreter)
                plugin['register_tag_handler']("pre", "title", "python_tutorial", insert_interpreter)
            vlam_load_local.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface
                requires: {"/local"}
                plugin['register_tag_handler']("span", "title", "load_local", insert_load_local)
            vlam_load_remote.py # tests :2.4, 2.5, 3.0a1, 3.0a2
                import: interface
                requires: {"/remote"}
                plugin['register_tag_handler']("span", "title", "load_remote", insert_load_remote)
    src/imports:
            c_turtle.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: None
            graphics.py
                import: interface
            math_graphics.py
                import: interface
            turtle_js.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
                import: interface, c_turtle
            turtle_tk.py  # empty file for now...
    src/tests:
            mocks.py # used only for testing
                import: interface

The following are not likely to be tested by us::
            
    src/element_tree:
            BeautifulSoup.py
                import: None
            ElementPath.py
                import: None
            ElementSoup.py
                import: BeautifulSoup, ElementTree
            ElementTree.py
                import: ElementPath
            HTMLTreeBuilder.py
                import: ElementTree




Design philosophy
-----------------

Talk about the design philosophy from the point of view of 

 - an end user
 - a tutorial writer
 - a developer
 

Future work
-----------

Whereas we should use the main site (code.google.com) and the "issues" as a repository for
desired features, this section can be used as a quick off-line reminder until it is
noted as an "issue".

  - debug "print" statements should be made more robust (like they are in cometIO.py); currently
    they can be interfered with apparently by changes to sys.stdout that occur while Crunchy
    is running.