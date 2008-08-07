vlam_pdb.py tests
================================

Tested successfully with Python  None (not tested) 

vlam_pdb.py is a plugin whose purpose is to insert an debugger in a page.  It has the following functions
that require testing:

1. register(): registers a tag handler and tow http handler.
2. Proto : encode or decode a crunchy pdb command's output 
3. 


0. Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

  >>> from src.interface import Element, plugin, config, python_version
  >>> plugin.clear()
  >>> plugin['session_random_id'] = 42
  >>> config.clear()
  >>> import src.plugins.vlam_pdb as vlam_pdb 
  >>> import src.tests.mocks as mocks
  >>> mocks.init()
  >>> site_security = {'trusted_url': 'trusted',
  ...                  'display_only_url': 'display normal'}
  >>> def get_security_level(url):
  ...     return site_security[url]
  >>> config['page_security_level'] = get_security_level

1.)  Test (Register)
------------------------------------

# Test - check that tag handler, and service have been registered

  >>> vlam_pdb.register()
  >>> mocks.registered_tag_handler['pre']['title']['pdb'] == vlam_pdb.pdb_widget_callback
  True
  >>> mocks.registered_http_handler['/pdb_start' + plugin['session_random_id']] == vlam_pdb.pdb_start_callback 
  True
  >>> mocks.registered_http_handler['/pdb_cmd' + plugin['session_random_id']] == vlam_pdb.pdb_command_callback 
  True


2.)  Test (Proto) 
------------------------------------

  >>> proto = vlam_pdb.Proto() 
  >>> msg = "<string>|1" 
  >>> proto.decode(proto.encode('crunchy_where', msg)) == ('crunchy_where', msg)
  True


