"""  power_browser.py plugin.

Allow the user to always insert a file/url browser at the top of a page.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, config, Element
import python_files
import rst
import vlam_load_local
import vlam_load_remote

_default_menu = None
_css = None

def register():
    """The register() function is required for all plugins.
       """
    plugin['register_tag_handler']("body", None, None, insert_browser)

def insert_browser(page, body, *dummy):
    '''Inserts a default file/url browser at the top of a page'''
    span = Element("span")
    span.text = ' '
    if config['power_browser'] == 'None':
        return
    elif config['power_browser'] == 'python':
        python_files.insert_load_python(page, span, 'dummy')
    elif config['power_browser'] == 'rst':
        rst.insert_load_rst(page, span, 'dummy')
    elif config['power_browser'] == 'local_html':
        vlam_load_local.insert_load_local(page, span, 'dummy')
    elif config['power_browser'] == 'remote_html':
        vlam_load_remote.insert_load_remote(page, span, 'dummy')
    else:  # unrecognized value; ignore
        return
    body.insert(0, span)
