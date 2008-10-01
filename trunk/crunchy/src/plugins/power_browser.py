"""  power_browser.py plugin.

Allow the user to always insert a file/url browser at the top of a page.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, config, Element
import python_files
import rst

def register(): # tested
    """The register() function is required for all plugins.
       """
    plugin['register_end_pagehandler'](insert_browser)

def insert_browser(page, *dummy): # tested
    '''Inserts a default file/url browser at the top of a page'''
    div = Element("div")
    div.text = ' '

    '''to do:  when restructuring is completed, change the code below to
       something like
    if config[page.username]['power_browser'] is None:
        return
    else:
        try:
            plugin[config[page.username]['power_browser']](page, div, 'dummy')
            page.body.insert(0, div)
        except KeyError:
            this should not happen
        except:
            this should definitely not happen
'''

    if config[page.username]['power_browser'] is None:
        return
    elif config[page.username]['power_browser'] == 'local_python':
        plugin['local_python'](page, div, 'dummy')
    elif config[page.username]['power_browser'] == 'rst':
        rst.insert_load_rst(page, div, 'dummy')
    elif config[page.username]['power_browser'] == 'local_html':
        plugin['local_html'](page, div, 'dummy')
    elif config[page.username]['power_browser'] == 'remote_html':
        plugin['remote_html'](page, div, 'dummy')
    else:  # unrecognized value; ignore
        return
    page.body.insert(0, div)
