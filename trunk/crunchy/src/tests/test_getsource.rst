getrource.py tests
===================

Settings things up.
-------------------

    >>> import os, sys
    >>> from src.interface import plugin, config, get_base_dir
    >>> plugin.clear()
    >>> config.clear()
    >>> config['crunchy_base_dir'] = "/crunchy"
    >>> import src.plugins.getsource as getsource
    >>> import src.tests.mocks as mocks
    >>> mocks.init()

Testing register()
---------------------

    >>> getsource.register()
    >>> mocks.registered_tag_handler['pre']['title']['getsource'] == getsource.get_source
    True

Testing get_tutorial_path()
----------------------------

    >>> page = mocks.Page()
    >>> page.url = "/this/file"
    >>> page.is_local = True
    >>> getsource.get_tutorial_path(page)#.replace(os.path.sep, "/")
    '/this/file'
    >>> page.is_local = False
    >>> page.is_from_root = True
    >>> getsource.get_tutorial_path(page)#.replace(os.path.sep, "/")
    '/crunchy/server_root/this/file'

Testing extract_module_information()
---------------------------------------

    >>> getsource.extract_module_information("getsource module")
    ('', 'module', 'module')
    >>> getsource.extract_module_information("getsource ../module.function")
    ('..', 'module', 'module.function')
    >>> getsource.extract_module_information("getsource ../src/../module.function.other")
    ('../src/..', 'module', 'module.function.other')

Creating fake file to play with
-------------------------------

    >>> cwd = os.getcwd()
    >>> sys.path.insert(0, cwd)
    >>> fake = """
    ... '''A test file for getsource.py'''
    ... def a_function(arg):
    ...     '''The docstring'''
    ...     pass
    ...
    ... class Fantastic(object):
    ...     def __init__(self):
    ...         print("Hello")
    ...     def bye(self):
    ...        print("Goodbye!")
    ... """
    >>> fname = "test"
    >>> fname_py = fname + ".py"
    >>> while fname_py in os.listdir(cwd):
    ...     fname += "_"
    ...     fname_py = fname + ".py"
    >>> f_open = open(fname_py, 'w')
    >>> f_open.write(fake)
    >>> f_open.close()



Remove the fake file to end
-------------------------------
    >>> os.remove(os.path.join(cwd, fname_py))