rst_directives.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

    >>> import src.plugins.rst_directives as directives

    >>> print(directives.extract_object_name(['a', 'b', 'c']))
    ('a', ['b', 'c'])


    >>> print(directives.extract_module_information("../src/module.function"))
    ('../src', 'module', 'module.function')
    >>> print(directives.extract_module_information("src/module.function.a.b"))
    ('src', 'module', 'module.function.a.b')
    >>> print(directives.extract_module_information("module"))
    ('', 'module', 'module')
