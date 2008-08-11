vlam_pdb.py tests
================================

Tested successfully with Python  None (not tested) 

vlam_pdb.py is a plugin whose purpose is to insert an debugger in a page.  It has the following functions
that require testing:

1. register(): registers a tag handler and tow http handler.
2. Proto : encode or decode a crunchy pdb command's output 
3. pdb_widget_callback  insert pdb widget into page 


0. Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

  >>> from src.interface import Element, plugin, config, python_version
  >>> plugin.clear()
  >>> plugin['session_random_id'] = "42"
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

# Test - check that tag handler

  >>> vlam_pdb.register()
  >>> mocks.registered_tag_handler['pre']['title']['pdb'] == vlam_pdb.pdb_widget_callback
  True
  >>> mocks.registered_http_handler['/pdb_start' + plugin['session_random_id']] == vlam_pdb.pdb_start_callback 
  True
  >>> mocks.registered_http_handler['/pdb_cmd' + plugin['session_random_id']] == vlam_pdb.pdb_command_callback 
  True
  >>> mocks.registered_http_handler['/pdb_js' + plugin['session_random_id'] + '.js'] == vlam_pdb.pdb_js_file_callback 
  True


2.)  Test (Proto) 
------------------------------------

  >>> proto = vlam_pdb.Proto() 
  >>> msg = "<string>|1" 
  >>> proto.decode(proto.encode('crunchy_where', msg)) == ('crunchy_where', msg)
  True

3.)  Test (pdb_widget_callback)
------------------------------------

First, we need to fake some services that are expected by pdb_widget_callback 

  >>> def style_pycode_nostrip(page, elem):
  ...  return "", "TestMarkup", None
  >>> def insert_editor_subwidget(page, elem, uid, code):
  ...  return
  >>> def insert_io_subwidget(page, elem, uid):
  ...  return
  >>> def register_io_hook(hook, func, uid):
  ...  return

# Create fake services from the above functions

  >>> class DummyServices(object):
  ...     def __init__(self):
  ...          self.style_pycode_nostrip = style_pycode_nostrip 
  ...          self.insert_editor_subwidget = insert_editor_subwidget
  ...          self.insert_io_subwidget = insert_io_subwidget
  ...          self.register_io_hook = register_io_hook 
  ...
  >>> plugin['services'] = DummyServices()

#Create fake page and insert the pdb widget

  >>> page = mocks.Page()
  >>> page.url = "trusted_url"
  >>> elem = Element("pre")
  >>> uid = "2:3"
  >>> vlam_pdb.pdb_widget_callback(page, elem, uid) 

#Test the result

  >>> print(page.added_info)
  ['includes', ('add_include', 'pdb_included'), ('insert_js_file', '/pdb_js42.js'), 'includes', ('add_include', 'pdb_css_code'), 'add_css_code']

#Test buttons
  
  >>> btns = elem.findall("button")
  >>> btns[0].attrib["onclick"] == "init_pdb('%s');" %(uid)
  True
  >>> btns[0].attrib["id"] == "btn_start_pdb_%s" %(uid)
  True

  >>> btns[1].attrib["id"] == "btn_next_step_%s" %(uid)
  True

  >>> btns[2].attrib["id"] == "btn_step_into_%s" %(uid)
  True

  >>> btns[3].attrib["id"] == "btn_return_%s" %(uid)
  True

  >>> elem.find("div").attrib["id"] == "local_ns_%s" %uid
  True

4.) Test (pdb_start_callback)
------------------------------------

  >>> plugin['exec_code'] = lambda code,uid:None 
  >>> code = """i=40
  ... j=2
  ... print i+j
  ... """
  >>> request = mocks.Request(data=code, args={'uid':uid})
  >>> vlam_pdb.pdb_start_callback(request)
  200
  End headers

5.) Test (pdb_command_callback)

  >>> request = mocks.Request(args={'uid':uid,'command':'next'})
  >>> vlam_pdb.pdb_start_callback(request)
  200
  End headers


6.) Test (pdb_filter)

  >>> def fake_exec_js(page_id, js): print(page_id, js)
  >>> plugin['exec_js'] = fake_exec_js 
  >>> data = "<span class='stdout'>non-pdb-output</span>"
  >>> print (data == vlam_pdb.pdb_filter(data, uid))
  True
  >>> proto = vlam_pdb.Proto()
  >>> after_filter = vlam_pdb.pdb_filter("<span class='stdout'>%s</span>" %(proto.encode('crunchy_locals', "some_pdb_output")), uid)
  ('2', "window['pdb_2:3'].update_local_ns('some_pdb_output');")
  >>> after_filter == ''
  True
  >>> after_filter = vlam_pdb.pdb_filter("<span class='stdout'>%s</span>" %(proto.encode('crunchy_where', "<string>|1")), uid)
  ('2', "window['pdb_2:3'].go_to_file_and_line('&lt;string&gt;','','1');")
  >>> after_filter == ''
  True
  
  >>> after_filter = vlam_pdb.pdb_filter("<span class='stdout'>%s</span>" %(proto.encode('crunchy_where', 'bad_file_name.py' + '|1')), uid)
  ('2', "window['pdb_2:3'].go_to_file_and_line('bad_file_name.py','#SORRY, SOURCE NOT AVAILABLE','1');")
  >>> after_filter == ''
  True

  create a fake file 

  >>> import os
  >>> file_content = "#This is just a test."
  >>> filename = "test_file0.txt"
  >>> filepath = os.path.join(os.getcwd(), filename)
  >>> handle = open(filepath, 'w')
  >>> __irrelevant = handle.write(file_content)
  >>> handle.close()

  >>> after_filter = vlam_pdb.pdb_filter("<span class='stdout'>%s</span>" %(proto.encode('crunchy_where', filename + '|1')), uid)
  ('2', "window['pdb_2:3'].go_to_file_and_line('test_file0.txt','#This is just a test.','1');")
  >>> after_filter == ''
  True
  >>> os.remove(filename)

