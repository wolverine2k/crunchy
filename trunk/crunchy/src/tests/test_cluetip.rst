cluetip.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

    >>> from src.interface import plugin, config, get_base_dir
    >>> plugin.clear()
    >>> config.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()
    >>> import src.plugins.cluetip
