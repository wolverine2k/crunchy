config_gui plugin tests
=======================

Setting things up:

    >>> from src.interface import from_comet
    >>> from_comet.clear()
    >>> def dummy(arg): pass
    >>> from_comet['register_new_page'] = dummy

    >>> from StringIO import StringIO
    >>> from src.interface import (
    ...     config, plugin, get_base_dir,
    ...     additional_menu_items, Element)
    >>> from src.interface import ElementTree as et
    >>> plugin.clear()
    >>> config.clear()
    >>> additional_menu_items.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()
    >>> import src.vlam as vlam
    >>> plugin['session_random_id'] = 42
    >>> import src.plugins.config_gui as config_gui

And our birthday boy:

    >>> import src.plugins.config_gui as config_gui

Stolen from the vlam tests:

    >>> def process_html(html):
    ...     fake_file = StringIO()
    ...     fake_file.write(html)
    ...     fake_file.seek(0)
    ...     page = vlam.BasePage('dummy_username')
    ...     page.create_tree(fake_file)  # tested separately below
    ...     return page


Test add_configuration_to_menu:

    >>> html = u'<html></html>'
    >>> page = process_html(html)
    >>> config_gui.add_configuration_to_menu(page)
    >>> assert 'preferences' in additional_menu_items
    >>> print(et.tostring(additional_menu_items['preferences']))
    <li><a href="/docs/basic_tutorial/preferences.html">Preferences</a></li>

Test insert_preferences:

    >>> html = u'<html></html>'
    >>> page = process_html(html)
    >>> elem = Element("div", title=u"fake")

But first, disable show:

    >>> config_gui.show = lambda *a: None
    >>> config_gui.insert_preferences(page, elem, 'fake uid')
    >>> assert page.includes("set_config")
    >>> print(et.tostring(elem))
    <div class="config_gui" title="fake"><table /></div>
