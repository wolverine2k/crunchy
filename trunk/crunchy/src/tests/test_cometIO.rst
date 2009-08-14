cometIO.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

    >>> from src.interface import plugin, config
    >>> plugin.clear()
    >>> config.clear()
    >>> from os import getcwd
    >>> config['crunchy_base_dir'] = getcwd()
    >>> import src.cometIO
