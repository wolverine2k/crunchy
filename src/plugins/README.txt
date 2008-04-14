README File for the Crunchy Plugins

--

CONTENTS:

1. The Plugin API

2. The included plugins

--

1. The Plugin API

The Plugin API is described at http://code.google.com/p/crunchy/wiki/CrunchyPluginAPI

--

2. The Included Plugins

	execution.py:
		handles the http execution callback "/exec".
		
	handle_default.py:
		Provides a default http request handler that looks up files in the tree
		
	io_widget.py:
		Provides a service ("io_subwidget") that inserts the IO widget.
		
	testplugins.py:
		Contains test case plugins for use with the test suite.
		
	vlam_doctest.py:
		Inserts the doctest widgets into vlam pages.
		
	vlam_editor.py:
		Inserts the simple editor widgets into vlam pages.
		Provides a service ("editor_subwidget") to insert text editors.
		
	vlam_interpreter.py
		inserts the interpreter widgets into vlam pages.