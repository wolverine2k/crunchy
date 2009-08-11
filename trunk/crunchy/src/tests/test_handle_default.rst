handle_default.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

    >>> from src.interface import plugin, config, get_base_dir
    >>> import os
    >>> plugin.clear()
    >>> config.clear()
    >>> base_dir = config['crunchy_base_dir'] = get_base_dir()
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> import src.plugins.handle_default as hd


testing register()
-------------------

    >>> hd.register()
    >>> mocks.registered_http_handler[None] == hd.handler
    True

testing annotate()
-------------------

    >>> server_root = os.path.join(base_dir, 'server_root')
    >>> hd.annotate(server_root, ['images', 'index.html'])
    ['images/', 'index.html']

testing ``get_directory``
--------------------------
This was created as a regression test out of Python 3's removal of
``dircache`` back in the gsoc_2009 branch, but it seems good enough to
keep here.

    >>> path = os.path.join(config['crunchy_base_dir'], 'server_root/css')
    >>> alist = hd.get_directory(path, 'Crunchy')
    >>> 'crunchy.css' in alist
    True
    >>> 'images/' in alist
    True

testing ``meta_content_open`
----------------------------
We use Unicode literals because doctest does weird things to actual
Unicode characters.

    >>> import sys
    >>> def unicode(text):
    ...    if sys.version_info[0] < 3:
    ...        # Lets us type unicode escapes even without the unicode.
    ...        return text.decode('unicode_escape')
    ...    return text

    >>> isopath = os.path.join(hd.root_path, 'docs', 'tests', 'iso-8859-1.html')
    >>> assert os.path.exists(isopath)
    >>> f = hd.meta_content_open(isopath)
    >>> assert unicode('Andr\xe9') in f.read()
    >>> f.close()

    >>> isopath = os.path.join(hd.root_path, 'docs', 'tests', 'utf-8.html')
    >>> assert os.path.exists(isopath)
    >>> f = hd.meta_content_open(isopath)
    >>> assert unicode('Andr\xe9') in f.read()
    >>> f.close()
