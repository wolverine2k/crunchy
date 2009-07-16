crunchy_sidebar plugin tests
============================

Setting things up:

    >>> import src.vlam as vlam
    >>> from StringIO import StringIO
    >>> from src.interface import (
    ...     config, plugin, get_base_dir,
    ...     additional_menu_items)
    >>> from src.interface import ElementTree as et
    >>> plugin.clear()
    >>> config.clear()
    >>> additional_menu_items.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()

Get a session_random_id value:

    >>> import src.CrunchyPlugin

And our birthday boy:

    >>> import src.plugins.crunchy_sidebar as sidebar

Stolen from the vlam tests:

    >>> def process_html(html):
    ...     fake_file = StringIO()
    ...     fake_file.write(html)
    ...     fake_file.seek(0)
    ...     page = vlam.BasePage('dummy_username')
    ...     page.create_tree(fake_file)
    ...     return page


Test insert_javascript:

    >>> html = u'<html></html>'
    >>> page = process_html(html)
    >>> sidebar.insert_javascript(page, 'dummy', 'dummy')
    >>> assert page.includes("jquery.dimensions.js")
    >>> assert page.includes("jquery.accordion.js")
