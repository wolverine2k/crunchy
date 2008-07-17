"""  power_browser.py plugin.

Allow the user to always insert a file/url browser at the top of a page.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, config, Element
import python_files
import rst
import vlam_load_local
import vlam_load_remote

def register(): # tested
    """The register() function is required for all plugins.
       """
    plugin['register_end_pagehandler'](insert_browser)

def insert_browser(page, *dummy): # tested
    '''Inserts a default file/url browser at the top of a page'''
    div = Element("div")
    div.text = ' '
    if config['power_browser'] is None:
        return
    elif config['power_browser'] == 'python':
        python_files.insert_load_python(page, div, 'dummy')
    elif config['power_browser'] == 'rst':
        rst.insert_load_rst(page, div, 'dummy')
    elif config['power_browser'] == 'local_html':
        vlam_load_local.insert_load_local(page, div, 'dummy')
    elif config['power_browser'] == 'remote_html':
        vlam_load_remote.insert_load_remote(page, div, 'dummy')
    else:  # unrecognized value; ignore
        return
    page.body.insert(0, div)
