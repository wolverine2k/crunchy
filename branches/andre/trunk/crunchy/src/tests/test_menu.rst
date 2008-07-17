menu.py tests
======================


Setting things up
------------------

    >>> from src.interface import config, plugin, tostring, translate
    >>> plugin.clear()
    >>> config.clear()
    >>> def dummy_add(*args):
    ...      for arg in args:
    ...          print arg
    >>> plugin['add_vlam_option'] = dummy_add
    >>> def repeat(msg):
    ...      return msg
    >>> translate['_'] = repeat
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> import src.plugins.menu as menu

Testing register()
===================

    >>> menu.register()
    menu_position
    top_left
    top_right
    bottom_right
    bottom_left
    >>> print(mocks.registered_end_pagehandlers) #doctest: +ELLIPSIS
    {'<function insert_menu ...>': <function insert_menu ...>}

Testing create_empty_menu()
============================

    >>> _menu, _menu_items = menu.create_empty_menu()
    >>> tostring(_menu)
    '<div class="menu"><ul><li>Crunchy Menu<ul /></li></ul></div>'
    >>> tostring(_menu_items)
    '<ul />'


Testing create_home()
=====================

    >>> home = menu.create_home()
    >>> tostring(home)
    '<li><a href="/index.html">Crunchy Home</a></li>'

Testing create_quit()
=====================

    >>> Quit = menu.create_quit()
    >>> tostring(Quit)
    '<li><a href="/exit">Quit Crunchy</a></li>'

Testing insert_menu()
======================

There are 4 valid options, and a default option for insert_menu(); all
yield the same results using our mock functions.  So, we only test one here.

    >>> page = mocks.Page()
    >>> page.body = ['dummy']
    >>> config['menu_position'] = 'top_right'
    >>> menu.insert_menu(page)
    >>> tostring(page.body[0]) #doctest: +ELLIPSIS
    '<div class="menu"...Crunchy Menu...Crunchy Home...Quit Crunchy...</div>'
    >>> page.added_info[0] == 'add_css_code'
    True

