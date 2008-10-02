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

    if config[page.username]['power_browser'] is None:
        return
    else:
        try:
            plugin[config[page.username]['power_browser']](page, div, 'dummy')
            page.body.insert(0, div)
        except: # unrecognized value, just ignore... (see below)
            return

# Why ignoring the exception?  Perhaps the browser requested is not available.
# For example, suppose the user upgrades to a new Python version but do not
# install docutils. As a result, she will not be able to process rst files.
# However, she could have set the configuration to include an rst browser
# while using a previous version of Python ...