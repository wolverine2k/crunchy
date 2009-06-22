handle_default.py tests
=======================

Setting things up:

    >>> import os.path
    >>> from src.interface import plugin, config, get_base_dir
    >>> plugin.clear()
    >>> config.clear()

    >>> def trust_me(url):
    ...    return 'trusted'
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['page_security_level'] = trust_me
    >>> config['crunchy_base_dir'] = get_base_dir()

    >>> from src.CrunchyPlugin import get_root_dir
    >>> plugin['get_root_dir'] = get_root_dir

And our debutante:

    >>> import src.plugins.handle_default as handle_default

Test ``list_directory``. This was created as a regression test out of
Python 3's removal of ``dircache``, whose most important contribution
was the annotation of directories with a forward slash. A downside is
that it depends on the contents of ``server_root/css``, so we limit
elide most of the output.

    >>> path = os.path.join(config['crunchy_base_dir'], 'server_root/css')
    >>> alist = handle_default.list_directory(path)
    >>> 'crunchy.css' in alist
    True
    >>> 'images/' in alist
    True
