crst2s5.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

    >>> import crst2s5

    >>> print(crst2s5.extract_object_name(['a', 'b', 'c']))
    ('a', ['b', 'c'])


    >>> print(crst2s5.extract_module_information("../src/module.function"))
    ('../src', 'module', 'module.function')
    >>> print(crst2s5.extract_module_information("src/module.function.a.b"))
    ('src', 'module', 'module.function.a.b')
    >>> print(crst2s5.extract_module_information("module"))
    ('', 'module', 'module')
