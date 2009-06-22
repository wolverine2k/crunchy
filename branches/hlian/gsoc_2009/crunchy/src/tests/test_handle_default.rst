handle_default.py tests
=======================

Setting things up:

    >>> from src.interface import plugin, config
    >>> def trust_me(url):
    ...    return 'trusted'
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['page_security_level'] = trust_me

Seed ``plugin`` and ``server``:

    >>> import src.CrunchyPlugin
    >>> import src.plugins.menu

And our debutante:

    >>> import src.plugins.handle_default as handle_default

Test ``list_directory``. This was created as a regression test out of
Python 3's removal of ``dircache``, whose most important contribution
was the annotation of directories with a forward slash. A downside is
that it depends on the contents of ``server_root/css``, so we limit
elide most of the output.

    >>> path = '/cygdrive/c/lab/crunchy/crunchy/server_root/css'
    >>> alist = handle_default.list_directory(path)
    >>> 'crunchy.css' in alist
    True
    >>> 'images/' in alist
    True
