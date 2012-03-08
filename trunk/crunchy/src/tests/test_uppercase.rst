uppercase.py tests
================================
Purpose: Plugin to convert lowercase text to uppercase.
Operates on:
    tag: bold related, viz.: b, em, strong
    attribute: title
    keyword: uppercase
Extra Feature: Uses jQuery to give the resultant text a fade effect.

Tested in Python 2.6.2

Setup.

    >>> from src.interface import plugin, config, get_base_dir, tostring, fromstring
    >>> plugin.clear()
    >>> config.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()
    >>> import src.plugins.uppercase as uppercase
    >>> import src.tests.mocks as mocks
    >>> mocks.init()

Register.

    >>> uppercase.register()
    >>> mocks.registered_tag_handler['b']['title']['uppercase'] # doctest:+ELLIPSIS
    <function insert_uppercase at ...>
    >>> mocks.registered_tag_handler['em']['title']['uppercase'] # doctest:+ELLIPSIS
    <function insert_uppercase at ...>
    >>> mocks.registered_tag_handler['strong']['title']['uppercase'] # doctest:+ELLIPSIS
    <function insert_uppercase at ...>

Create mock input.

    >>> page = mocks.Page()
    >>> e1 = fromstring('<b title="uppercase">the <u>cat <i>sat</i> on</u> the mat</b>')
    >>> uid = '420_480'

Should convert all text elements to uppercase and add some js and css code.

    >>> uppercase.insert_uppercase(page, e1, uid)
    >>> tostring(e1)
    u'<b class="420_480" title="uppercase">THE <u>CAT <i>SAT</i> ON</u> THE MAT</b>'
    >>> page.added_info
    ['includes', ('add_include', 'uppercaseEffect'), 'add_js_code', 'add_css_code', 'add_js_code']

Ensure that plugin is safe for tags without a text node.

    >>> e2 = fromstring('<b title="uppercase"></b>')
    >>> uppercase.insert_uppercase(page, e2, uid)
    >>> tostring(e2)
    u'<b class="420_480" title="uppercase"></b>'
