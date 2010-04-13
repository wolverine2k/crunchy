"""  power_browser.py plugin.

Allow the user to always insert a file/url browser at the top of a page.
Also includes a link to the browsers page in the menu.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, config, Element, SubElement, translate, \
   additional_menu_items
_ = translate['_']

import traceback

def register(): # tested
    """The register() function is required for all plugins.
       """
    plugin['register_end_pagehandler'](insert_browser)
    plugin['register_begin_pagehandler'](add_browsing_to_menu)

def add_browsing_to_menu(dummy):
    '''adds a menu item allowing the user to go the the browsers page'''
    menu_item = Element("li")
    link = SubElement(menu_item, 'a', href="/docs/basic_tutorial/browsing.html")
    link.text = _("Browsing")
    additional_menu_items['browsing'] = menu_item

def insert_browser(page, *dummy): # tested
    '''Inserts a default file/url browser at the bottom of a page'''
    div = Element("div")
    div.text = ' '

    browser = plugin.get(config[page.username]['power_browser'])
    if not browser:
        return

    try:
        browser(page, div, 'dummy')
        page.body.append(div)
    except:
        print(traceback.format_exc())
        return
