"""  Crunchy load local tutorial plugin.

Creates a form allowing to browse for a local tutorial to be loaded
by Crunchy.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API
import CrunchyPlugin

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
    CrunchyPlugin.register_vlam_handler("span", "load_local", insert_load_local)

def insert_load_local(page, parent, uid, vlam):
    name1 = 'browser_'
    name2 = 'submit_'
    form1 = CrunchyPlugin.SubElement(parent, 'form', name=name1,
                        onblur = "document.%s.url.value="%name2+\
                        "document.%s.filename.value"%name1)
    input1 = CrunchyPlugin.SubElement(form1, 'input', type='file',
                 name='filename', size='80')
    br = CrunchyPlugin.SubElement(form1, 'br')

    form2 = CrunchyPlugin.SubElement(parent, 'form', name=name2, method='get',
                action='/local')
    input2 = CrunchyPlugin.SubElement(form2, 'input', type='hidden', name='url')
    input3 = CrunchyPlugin.SubElement(form2, 'input', type='submit',
             value='Load local tutorial')
    input3.attrib['class'] = 'crunchy'