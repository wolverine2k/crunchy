getrource.py tests
===================

Settings things up.
-------------------

    >>> import os, sys
    >>> from src.interface import plugin, config, get_base_dir
    >>> plugin.clear()
    >>> config.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()
    >>> import src.plugins.getsource as getsource
    >>> import src.tests.mocks as mocks
    >>> mocks.init()

Testing register()
---------------------

    >>> getsource.register()
    >>> mocks.registered_tag_handler['div']['title']['getsource'] == getsource.get_source
    True

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