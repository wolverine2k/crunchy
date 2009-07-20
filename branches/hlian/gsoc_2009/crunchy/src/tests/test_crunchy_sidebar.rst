crunchy_sidebar plugin tests
============================

Setting things up:

    >>> from src.interface import from_comet
    >>> from_comet.clear()
    >>> def dummy(arg): pass
    >>> from_comet['register_new_page'] = dummy

    >>> from StringIO import StringIO
    >>> from src.interface import (
    ...     config, plugin, get_base_dir,
    ...     additional_menu_items)
    >>> from src.interface import ElementTree as et
    >>> plugin.clear()
    >>> config.clear()
    >>> additional_menu_items.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()
    >>> import src.vlam as vlam

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
