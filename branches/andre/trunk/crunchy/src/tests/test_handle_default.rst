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