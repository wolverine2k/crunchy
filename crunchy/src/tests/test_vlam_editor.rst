vlam_editor.py tests
================================

vlam_editor.py is a plugin whose purpose is to insert an editor in a page (calling
editarea.py for some functions in doing so).  It has the following functions
that require testing:

#. `register()`_
#. kill_thread_handler()
#. `insert_editor_subwidget()`_
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
  >>> plugin['session_random_id'] = 42
  >>> config.clear()
  >>> config['editarea_language'] = 'en'
  >>> import src.plugins.vlam_editor as vlam_editor 
  >>> import src.plugins.editarea
  >>> import src.tests.mocks as mocks
  >>> mocks.init()
  >>> site_security = {'trusted_url': 'trusted',
  ...                  'display_only_url': 'display normal'}
  >>> def get_security_level(url):
  ...     return site_security[url]
  >>> config['page_security_level'] = get_security_level

.. _`register()`:

Testing register()
------------------------------------

# Test - check that tag handler, and service have been registered

  >>> vlam_editor.register()
  >>> mocks.registered_tag_handler['pre']['title']['editor'] == vlam_editor.insert_editor
  True
  >>> mocks.registered_tag_handler['pre']['title']['alternate_python_version'] == vlam_editor.insert_alternate_python
  True
  >>> mocks.registered_tag_handler['pre']['title']['alt_py'] == vlam_editor.insert_alternate_python
  True
  >>> mocks.registered_services['insert_editor_subwidget'] == vlam_editor.insert_editor_subwidget
  True

.. _`insert_editor_subwidget()`:

Testing insert_editor_subwidget()
------------------------------------

First, we need to fake some services that are expected by insert_editor_subwidget

  >>> def style_pycode(page, elem):
  ...  return "", "TestMarkup", None

# Used as a fake insert_io_subwidget function

  >>> def insert_io_subwidget(page, elem, uid):
  ...  return

# Create fake services from the above functions

  >>> class DummyServices(object):
  ...     def __init__(self):
  ...          self.style_pycode = style_pycode
  ...          self.insert_io_subwidget = insert_io_subwidget
  ...          self.enable_editarea = src.plugins.editarea.enable_editarea
  ...          self.insert_editor_subwidget = vlam_editor.insert_editor_subwidget # tested above
  ...
  >>> plugin['services'] = DummyServices()

Create also a fake configuration variable.

  >>> config['temp_dir'] = 'temp_dir'

# Next, we need to create a fake page that we will process. 

  >>> page = mocks.Page()
  >>> elem = Element("pre")
  >>> uid = "2"
  >>> vlam_editor.insert_editor_subwidget(page, elem, uid) 

# Test the Results

  >>> print(page.added_info)
  ['includes', ('add_include', 'editarea_included'), 'add_js_code', ('insert_js_file', '/edit_area/edit_area_crunchy.js'), 'includes', ('add_include', 'hidden_load_and_save'), 'add_css_code', 'add_js_code']
  >>> elem[0].tag == "textarea"
  True

# Test - hidden_load

  >>> elem[1].tag == "div"
  True
  >>> elem[1].attrib == {'id': 'hidden_loadcode_2', 'class': 'load_python'}
  True

# Test - hidden_load/br

  >>> elem[1][0].tag == "br"
  True

# Test - hidden_load/form1
  >>> elem[1][1].tag == "form"
  True

  >>> elem[1][1].attrib == {'onblur': "a=getElementById('pathhidden_loadcode_2');b=getElementById('filenamehidden_loadcode_2');a.value=b.value"}
  True

# Test - hidden_load/form1/input1

  >>> elem[1][1][0].tag == "input"
  True
  >>> elem[1][1][0].attrib == {'type': 'file', 'id': 'filenamehidden_loadcode_2', 'size': '80'}
  True

# Test - hidden_load/form1/br

  >>> elem[1][1][1].tag == "br"
  True

# Test - hidden_load/form2

  >>> elem[1][2].tag == "form"
  True

# Test - hidden_load/form2/input2

  >>> elem[1][2][0].tag == "input"
  True
  >>> elem[1][2][0].attrib == {'type': 'hidden', 'id': 'pathhidden_loadcode_2'}
  True

# Test - hidden_load/btn

  >>> elem[1][3].tag == "button"
  True
  >>> elem[1][3].attrib == {'onclick': "c=getElementById('pathhidden_loadcode_2');path=c.value;load_python_file('code_2');"}
  True

# Test - hidden_load/btn2

  >>> elem[1][4].tag == "button"
  True
  >>> elem[1][4].attrib == {'onclick': "c=getElementById('hidden_loadcode_2');path=c.style.visibility='hidden';c.style.zIndex=-1;"}
  True

##
## start test on add_hidden_load_and_save / addSavePython
##

# Test - hidden_save

  >>> elem[2].tag == "div"
  True
  >>> elem[2].attrib == {'id': 'hidden_savecode_2', 'class': 'save_python'}
  True

# Test - hidden_save/br

  >>> elem[2][0].tag == "br"
  True

# Test - hidden_save/form1

  >>> elem[2][1].tag == "form"
  True

# Test = hidden_save/form1/input1

  >>> elem[2][1][0].tag == "input"
  True
  >>> elem[2][1][0].attrib == {'type': 'file', 'id': 'filenamehidden_savecode_2', 'size': '80'}
  True

# Test - hidden_save/form1/br

  >>> elem[2][1][1].tag == "br"
  True

# Test - hidden_save/form2

  >>> elem[2][2].tag == "form"
  True

# Test - hidden_save/form2/input2

  >>> elem[2][2][0].tag == "input"
  True
  >>> elem[2][2][0].attrib == {'type': 'hidden', 'id': 'pathhidden_savecode_2'}
  True

# Test - hidden_save/btn

  >>> elem[2][3].tag == "button"
  True
  >>> elem[2][3].attrib == {"onclick": "a=getElementById('pathhidden_savecode_2');b=getElementById('filenamehidden_savecode_2');a.value=b.value;c=getElementById('pathhidden_savecode_2');path=c.value;save_python_file(path,'code_2');"}
  True

# Test - hidden_save/btn2

  >>> elem[2][4].tag == "button"
  True
  >>> elem[2][4].attrib == {'onclick': "c=getElementById('hidden_savecode_2');path=c.style.visibility='hidden';c.style.zIndex=-1;"}
  True

# Test - hidden_save/btn3

  >>> elem[2][5].tag == "button"
  True
  >>> elem[2][5].attrib == {'onclick': "a=getElementById('pathhidden_savecode_2');b=getElementById('filenamehidden_savecode_2');a.value=b.value;c=getElementById('pathhidden_savecode_2');path=c.value;save_and_run(path,'code_2');"}
  True

.. _`insert_editor()`:

Testing  insert_editor()
------------------------------------

#  Create Objects needed

  >>> page = mocks.Page()
  >>> elem = Element("pre")
  >>> uid = "2"

Set object attributes for an untrusted page

  >>> page.url = "display_only_url"
  >>> elem.attrib = {'title': 'no_pre'}

Run the Function

  >>> vlam_editor.insert_editor(page, elem, uid) 

Test - check to make sure functions in page were called

  >>> print(page.added_info)
  ['includes', ('add_include', 'editarea_included'), 'add_js_code', ('insert_js_file', '/edit_area/edit_area_crunchy.js'), 'includes', ('add_include', 'hidden_load_and_save'), 'add_css_code', 'add_js_code']

Repeat, this time for a trusted page; the code for execution should be 
included this time.

  >>> page.url = "trusted_url"
  >>> page.added_info = []
  >>> elem.attrib = {'title': 'no_pre'}

#  Run the Function

  >>> vlam_editor.insert_editor(page, elem, uid) 

# Test - check to make sure functions in page were called

  >>> print(page.added_info)
  ['includes', ('add_include', 'exec_included'), 'add_js_code', 'includes', ('add_include', 'editarea_included'), 'add_js_code', ('insert_js_file', '/edit_area/edit_area_crunchy.js'), 'includes', ('add_include', 'hidden_load_and_save'), 'add_css_code', 'add_js_code']


# Test - elem

  >>> elem.tag == "div"
  True
  >>> elem.attrib == {'class': 'editor', 'id': 'div_2'}
  True

# Test - br

  >>> elem[3].tag == "br"
  True

# Test - button

  >>> elem[4].tag == "button"
  True
  >>> elem[4].attrib == {"onclick": "exec_code('2')"}
  True

# Test - span

  >>> elem[5].tag == "span"
  True
  >>> elem[5].attrib == {'style': 'display:none', 'id': 'path_2'}
  True
  >>> elem[5].text == config['temp_dir'] + vlam_editor.os.path.sep + "temp.py"
  True

# Test - br

  >>> elem[6].tag == "br"
  True
