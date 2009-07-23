vlam_editor.py tests
================================

vlam_editor.py is a plugin whose purpose is to insert an editor in a page (calling
editarea.py for some functions in doing so).  It has the following functions
that require testing:

#. `register()`_
#. kill_thread_handler()
#. insert_bare_editor()
#. `insert_editor()`_
#. insert_alternate_python()
#. insert_markup()


Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

  >>> from src.interface import Element, plugin, config
  >>> plugin.clear()
  >>> def dummy_add(*args):
  ...      for arg in args:
  ...          print arg
  >>> plugin['add_vlam_option'] = dummy_add
  >>> plugin['session_random_id'] = 42
  >>> config.clear()
  >>> config['Crunchy'] = {}
  >>> config['Crunchy']['editarea_language'] = 'en'

Note: we should have a test when the following is True.
  >>> config['Crunchy']['popups'] = False
  >>> import src.plugins.vlam_editor as vlam_editor 
  >>> import src.plugins.editarea
  >>> import src.tests.mocks as mocks
  >>> mocks.init()
  >>> site_security = {'trusted_url': 'trusted',
  ...                  'display_only_url': 'display normal'}
  >>> def get_security_level(url):
  ...     return site_security[url]
  >>> config['Crunchy']['page_security_level'] = get_security_level

.. _`register()`:

Testing register()
------------------------------------

# Test - check that tag handler, and service have been registered

    >>> vlam_editor.register()
    no_markup
    editor
    alternate_python_version
    alt_py

    >>> mocks.registered_tag_handler['pre']['title']['editor'] == vlam_editor.insert_editor
    True
    >>> mocks.registered_tag_handler['pre']['title']['alternate_python_version'] == vlam_editor.insert_alternate_python
    True
    >>> mocks.registered_tag_handler['pre']['title']['alt_py'] == vlam_editor.insert_alternate_python
    True
    >>> mocks.registered_services['insert_editor_subwidget'] == vlam_editor.insert_editor_subwidget
    True

.. _`insert_editor_subwidget()`:




