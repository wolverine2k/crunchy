"""  Crunchy load local tutorial plugin.

Creates a form allowing to browse for a local tutorial to be loaded
by Crunchy.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, SubElement

# The set of other "widgets/services" required from other plugins
requires = set(["/local"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register a single type of 'action':
          a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       """
    # 'load_remote' only appears inside <span> elements, using the notation
    # <span title='load_remote'>
    plugin['register_tag_handler']("span", "title", "load_local",
                                                 insert_load_local)

def insert_load_local(dummy_page, parent, dummy_uid):
    # in general, page and uid are used by similar plugins, but they are
    # redundant here.
    name1 = 'browser_'
    name2 = 'submit_'
    form1 = SubElement(parent, 'form', name=name1,
                        onblur = "document.%s.url.value="%name2+\
                        "document.%s.filename.value"%name1)
    SubElement(form1, 'input', type='file',
                 name='filename', size='80')
    SubElement(form1, 'br')

    form2 = SubElement(parent, 'form', name=name2, method='get',
                action='/local')
    SubElement(form2, 'input', type='hidden', name='url')
    input3 = SubElement(form2, 'input', type='submit',
             value='Load local tutorial')
    input3.attrib['class'] = 'crunchy'