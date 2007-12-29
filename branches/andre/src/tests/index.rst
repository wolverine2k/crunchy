Boring Work
===========

Crunchy is getting a bit big and, as of December 28, 2007, its module are too interdependent.
It is time for cleaning up and reorganizing things slightly before moving further.  This document
is a roadmap of things that should be done as well as a repository for ideas for future development.

It is intended to be a living document, updated as we go along.

It has three main sections:

 - Reducing dependencies & Testing
 - Design philosophy
 - Future work

Reducing dependencies & Testing
-------------------------------

Keep track of all modules and their dependencies; see if we can reduce the interdependencies.
This would make it much easier to reorganize the code if needed.  The way to do so is via
the interface.py module.  This document helps to keep track of how far we are along this processus.

All modules should be unit tested; we preferably use doctest-based unit tests that can be
used as supplementary documentation.

Crunchy includes a number of doctest based (.rst files) unit files which it can style 
and display, using the default crunchy.no_markup option.  (We suggest to use "python_code"
as that option when viewing these files).  These tests can be run via

- python all_tests.py, if using a Python version less than 3.0
- python all_tests_py3k.py, if using a Python version 3.x

In terms of test coverage, this is just a first draft which needs to be verified.

As a rule, every plugin should import the interface module - and
nothing else other than other plugins (and, perhaps, utilities.py) and/or modules from the Python standard library.  We keep track of the work that has been done by indicating the modules imported.

Crunchy Python files listing::

	all_tests.py
	all_tests_py3k.py
	crunchy.py
	    -> interface, http_serve, pluginloader
	src:
		cometIO.py
		    -> configuration, interpreter, interface, utilities
		configuration.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
		    -> translation, interface
		CrunchyPlugin.py
		    -> cometIO, PluginServices, translation, interface, vlam
		errors.py
		    -> configuration, translation
		http_serve.py
		    -> CrunchyPlugin, interface
		interface.py # tests :2.4, 2.5, 3.0a1, 3.0a2
		    -> tools_2k, tools_3k,  my_htmlentitydefs, translation, ElementTree++
		interpreter.py
		    -> interface, utilities, translation, configuration, errors
		my_htmlentitydefs.py
		    -> None
		pluginloader.py   # partial tests: 2.4, 2.5, 3.0a1
		    -> CrunchyPlugin  [and loads all the plugins]
		PluginServices.py
		    -> None
		security.py
		    -> interface, configuration
		tools_2k.py
		    -> errors
		tools_3k.py
		    -> None
		translation.py
		    -> interface
		utilities.py # tests :2.4, 2.5, 3.0a1, 3.0a2
		    -> interface
		vlam.py
		    -> security, interface, ElementSoup, cometIO, 
		       configuration, utilities
               
	src/plugins:
			c_turtle.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
			    -> None
			colourize.py # tests: 2.4, 2.5, 3.0a1?
			    -> CrunchyPlugin, interface, utilities
			comet.py
			    -> CrunchyPlugin, cometIO
			editarea.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
			    -> CrunchyPlugin, interface
			execution.py
			    -> CrunchyPlugin
			file_service.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
			    -> CrunchyPlugin, interface, configuration
			graphics.py
			    -> CrunchyPlugin
			handle_default.py (cp)
			    -> CrunchyPlugin, interface
			handle_local.py
			    -> CrunchyPlugin, interface
			handle_remote.py
			    -> CrunchyPlugin
			io_widget.py
			    -> CrunchyPlugin, editarea, interface
			links.py
			    -> CrunchyPlugin
			math_graphics.py
			    -> CrunchyPlugin
			menu.py
			    -> CrunchyPlugin, security
			rst.py
			    -> CrunchyPlugin
			security_advisor.py
			    -> CrunchyPlugin, interface
			tooltip.py
			    -> CrunchyPlugin, interface, interpreter
			turtle_js.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
			    -> CrunchyPlugin, c_turtle
			turtle_tk.py  # empty file for now...
			vlam_doctest.py
			    -> CrunchyPlugin, interface, utilities
			vlam_editor.py  # tests: 2.4, 2.5, 3.0a1, 3.0a2
			    -> CrunchyPlugin, configuration, utilities
			vlam_image_file.py
			    -> CrunchyPlugin, configuration
			vlam_interpreter.py
			    -> CrunchyPlugin, configuration, utilities, colourize
			vlam_load_local.py # tests: 2.4, 2.5, 3.0a1, 3.0a2
			    -> CrunchyPlugin
			vlam_load_remote.py # tests :2.4, 2.5, 3.0a1, 3.0a2
			    -> CrunchyPlugin

The following are not likely to be tested by us::
			
	src/element_tree:
			BeautifulSoup.py
			    -> None
			ElementPath.py
			    -> None
			ElementSoup.py
			    -> BeautifulSoup, ElementTree
			ElementTree.py
			    -> ElementPath
			HTMLTreeBuilder.py
			    -> ElementTree


The following are the actual links to existing test files.

#. test_c_turtle.rst_
#. test_colourize.rst_
#. test_configuration.rst_
#. test_editarea.rst_
#. test_file_service.rst_
#. test_pluginloader.rst_
#. test_turtle_js.rst_
#. test_interface.rst_
#. test_utilities.rst_
#. test_vlam_editor.rst_
#. test_vlam_load_local.rst_
#. test_vlam_load_remote.rst_

.. _test_c_turtle.rst: test_c_turtle.rst
.. _test_colourize.rst: test_colourize.rst
.. _test_configuration.rst: test_configuration.rst
.. _test_editarea.rst: test_editarea.rst
.. _test_file_service.rst: test_file_service.rst
.. _test_pluginloader.rst: test_pluginloader.rst
.. _test_turtle_js.rst: test_turtle_js.rst
.. _test_interface.rst: test_interface.rst
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