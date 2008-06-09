"""  Crunchy load local tutorial plugin.

Creates a form allowing to browse for a local tutorial to be loaded
by Crunchy.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin
from src.utilities import insert_file_browser

# The set of other "widgets/services" required from other plugins
requires = set(["/local"])

def register():  # tested
    """The register() function is required for all plugins.
       In this case, we need to register a single type of 'action':
          a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       """
    # 'load_remote' only appears inside <span> elements, using the notation
    # <span title='load_remote'>
    plugin['register_tag_handler']("span", "title", "load_local",
                                                 insert_load_local)

def insert_load_local(dummy_page, parent, dummy_uid):  # tested
    "Inserts a javascript browser object to load a local (html) file."
    insert_file_browser(parent, 'Load local html tutorial', '/local')
    return
