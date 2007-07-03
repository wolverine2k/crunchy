"""  Menu plugin.

Other than through a language preference, Crunchy menus can be modified
by tutorial writers using a custom meta declaration.
"""

import os

# All plugins should import the crunchy plugin API
import CrunchyPlugin
from element_tree import ElementTree, HTMLTreeBuilder

_default_menu = None
_css = None


def register():
    """The register() function is required for all plugins.
       """
    CrunchyPlugin.register_vlam_handler("meta", "menu", insert_special_menu)
    CrunchyPlugin.register_vlam_handler("no_tag", "menu", insert_default_menu)

def insert_special_menu(page, dummy_elem, uid, vlam):
    '''inserts a menu different from the Crunchy default based.
       The instruction is contained in a <meta> element and includes the
       filename where the menu is defined.'''
    raise NotImplementedError
    # Reminder:
    # When this function is implemented, we'll need to do the following.
    if not page.includes("menu_included"):
        page.add_include("menu_included")

def insert_default_menu(page):
    """inserts the default Crunchy menu"""
    global _default_menu, _css
    if _default_menu is None:  # Note: for now we only assume we have
                              # one default menu (in English)
                              # This will need to be changed later.
        menu_file = os.path.join(CrunchyPlugin.get_data_dir(),
                                 "server_root", "menu_en.html")
        _default_menu, _css = extract_menu(menu_file)
    page.body.insert(0, _default_menu)
    page.head.insert(0, _css)


def extract_menu(filename):
    '''extract a menu and css information from an html file.

       It assumes that the menu (usually an unordered list) is
       contained within the only <div> present in the file
       whereas the css information is contained in the single
       <link> in that file.'''
    try:
        tree = HTMLTreeBuilder.parse(filename)
    except Exception, info:
        print info
    # extract menu for use in other files
    #body = tree.find("body")
    menu = tree.find(".//div")
    #head = tree.find("head")
    css = tree.find(".//link")
    return menu, css

