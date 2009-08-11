security_advisor plugin tests
=============================

Setting things up:

    >>> from StringIO import StringIO
    >>> from src.interface import (
    ...     config, plugin, get_base_dir,
    ...     additional_menu_items)
    >>> from src.interface import ElementTree as et
    >>> plugin.clear()
    >>> config.clear()
    >>> additional_menu_items.clear()

    >>> def trust_me(url):
    ...    return 'trusted'
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['page_security_level'] = trust_me
    >>> config['Crunchy']['local_security'] = u'trusted'
    >>> config['crunchy_base_dir'] = get_base_dir()

    >>> import src.vlam as vlam

Because of our fake URL of 'test_security_advisor.rst', the netloc in
security_advisor.py is just the empty string. Since we want to trigger
that conditional code path, we include it in site_security below.

    >>> config['Crunchy']['site_security'] = ['']

More setup for globals:

    >>> import src.CrunchyPlugin

And our birthday boy:

    >>> import src.plugins.security_advisor as sa

Stolen from the vlam tests:

    >>> def process_html(html):
    ...     fake_file = StringIO()
    ...     fake_file.write(html)
    ...     fake_file.seek(0)
    ...     page = vlam.CrunchyPage(fake_file,
    ...         'test_security_advsior.rst',
    ...         'Crunchy')
    ...     return page


Test create_security_menu_item:

    >>> html = u'<html></html>'
    >>> page = process_html(html)
    >>> page.security_info = dict(level='display')
    >>> sa.create_security_menu_item(page)
    >>> assert 'security_report' in additional_menu_items
    >>> assert u'images/display.png' in et.tostring(additional_menu_items['security_report'])

Test insert_security_info as a whole:

    >>> html = u'<html><body><p>test_security_advisor</p></body></html>'
    >>> page = process_html(html)
    >>> page.find_body()
    >>> page.security_info = dict(level='display')
    >>> page.security_info['tags removed'] = []
    >>> page.security_info['attributes removed'] = []
    >>> page.security_info['styles removed'] = []
    >>> sa.insert_security_info(page)
    >>> assert u'traceback' not in page.read().lower()
