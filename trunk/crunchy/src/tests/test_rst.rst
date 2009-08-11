rst.py tests
================================

rst.py is a plugin whose purpose is to create a form allowing a user to browse
for a local tutorial written in reStructuredText to be loaded by Crunchy.

It contains two functions that need to be tested:
1. register()
2. insert_load_rst()

A third function, load_rst(), requires to read some file; for this reason,
we will not, for the moment, create a test for it, but rely instead on
some functional testing that we do on a regular basis.

0. Setting things up
--------------------

We need to import the plugin, something to create an Element, and
set up some dummy registering functions.

   >>> import os
   >>> from src.interface import config, Element, plugin, crunchy_bytes
   >>> from src.CrunchyPlugin import create_vlam_page

   >>> def trust_me(url):
   ...    return 'trusted'
   >>> config['Crunchy'] = {}
   >>> config['Crunchy']['page_security_level'] = trust_me

   >>> def dummy_add(*args):
   ...      for arg in args:
   ...          print(arg)
   >>> plugin.clear()
   >>> plugin['add_vlam_option'] = dummy_add
   >>> plugin['create_vlam_page'] = create_vlam_page

   >>> import src.tests.mocks as mocks
   >>> mocks.init()

   >>> import src.plugins.rst as rst

Note that if docutils is not installed for the Python version we are testing,
some tests would normally fail; we prevent this from happening by setting up
an appropriate flag.

   >>> _docutils_installed = True
   >>> try:
   ...     from docutils.core import publish_string
   ... except:
   ...     _docutils_installed = False

1. Testing register()
---------------------

# Test - check that tag handler, and service have been registered
    >>> if _docutils_installed:
    ...     rst.register()
    ... else:
    ...     print("power_browser")
    ...     print("rst")
    power_browser
    rst
    >>> if _docutils_installed:
    ...     print(mocks.registered_tag_handler['div']['title']['local_rst_file'] == rst.insert_load_rst)
    ...     print(mocks.registered_http_handler['/rst'] == rst.load_rst)
    ... else:
    ...     print(True)
    ...     print(True)
    True
    True

Check if the rst plugin handles non-local paths properly.

    >>> url = 'http://crunchy.googlecode.com/svn/trunk/crunchy/src/tests/how_to.rst'
    >>> assert rst.convert_rst(url, local=False)

Unfortunately, that code path isn't actually exposed in Crunchy at
all. (Nobody ever calls convert_rst with a local=False except this
test.) However, loading RST files from a local file is, so let's test
that entire path as well.

    >>> doc = """Hello\n=====\nThis is a *test*.""".encode()
    >>> import tempfile
    >>> f = tempfile.NamedTemporaryFile(mode='wb', delete=False)
    >>> irrelevant = f.write(crunchy_bytes(doc))
    >>> f.close()
    >>> request = mocks.Request(args={'url': f.name})
    >>> rst.load_rst(request)
    >>> os.remove(f.name)

    >>> body = ''.encode().join(request.wfile.lines).decode('utf8')
    >>> assert '<h1 class="title">Hello</h1>' in body
    >>> assert '<em>test</em>' in body
