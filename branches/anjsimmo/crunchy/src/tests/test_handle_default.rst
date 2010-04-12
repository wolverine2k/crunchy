handle_default.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

    >>> import codecs
    >>> import os
    >>> import src.tests.mocks as mocks
    >>> from src.interface import plugin, config, server, get_base_dir
    >>> from src.interface import crunchy_unicode, crunchy_bytes

    >>> plugin.clear()
    >>> config.clear()
    >>> server.clear()

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
    >>> os.path.exists(isopath)
    True
    >>> f = hd.meta_content_open(isopath)
    >>> unicode('Andr\xe9') in f.read()
    True
    >>> f.close()

    >>> isopath = os.path.join(hd.root_path, 'docs', 'tests', 'utf-8.html')
    >>> os.path.exists(isopath)
    True
    >>> f = hd.meta_content_open(isopath)
    >>> unicode('Andr\xe9') in f.read()
    True
    >>> f.close()

testing path_to_filedata
------------------------

    >>> def u(text):
    ...     """Allows us to write Unicode literals even in Python 2 bytestrings."""
    ...     if isinstance(text, crunchy_unicode): return text
    ...     else: return text.decode('unicode_escape')

Code path: the server exit.

    >>> server['exit'] = u('/exit')
    >>> server['server'] = mocks.Server()
    >>> data = hd.path_to_filedata(u('/exit'), hd.root_path)
    >>> isinstance(data, crunchy_bytes)
    True
    >>> 'exited' in data.decode('utf8')
    True

Code path: the invalid path.

    >>> data = hd.path_to_filedata(u('/../../../usr/local/bin'), hd.root_path)
    >>> isinstance(data, crunchy_bytes)
    True
    >>> '404' in data.decode('utf8')
    True

Code path: the directory listing without a trailing slash.

    >>> data = hd.path_to_filedata(u('/css'), hd.root_path)
    >>> data is None
    True

Code path: the directory listing.

    >>> data = hd.path_to_filedata(u('/css/'), hd.root_path)
    >>> isinstance(data, crunchy_bytes)
    True
    >>> 'crunchy.css' in data.decode('utf8')
    True

Code path: an .html page.

    >>> def trivial_vlam_page(file_handle, url, username):
    ...    return codecs.open(os.path.join(hd.root_path, url[1:]), 'r', 'utf8')
    >>> plugin['create_vlam_page'] = trivial_vlam_page

    >>> data = hd.path_to_filedata(u('/index.html'), hd.root_path)
    >>> isinstance(data, crunchy_bytes)
    True
    >>> 'Welcome' in data.decode('utf8')
    True

Code path: a binary file.

    >>> data = hd.path_to_filedata(u('/images/crunchy-python-powered.png'), hd.root_path)
    >>> isinstance(data, crunchy_bytes)
    True
