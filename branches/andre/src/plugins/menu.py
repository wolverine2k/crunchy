"""  Menu plugin.

Other than through a language preference, Crunchy menus can be modified
by tutorial writers using a custom meta declaration.
"""

import os

# All plugins should import the crunchy plugin API
import src.CrunchyPlugin as CrunchyPlugin
import src.security as security
import src.configuration as configuration

_default_menu = None
_css = None

def register():
    """The register() function is required for all plugins.
       """
    CrunchyPlugin.register_tag_handler("meta", "name", "crunchy_menu", insert_special_menu)
    CrunchyPlugin.register_tag_handler("no_tag", "menu", None, insert_default_menu)

def insert_special_menu(page, elem, dummy):
    '''inserts a menu different from the Crunchy default based.
       The instruction is contained in a <meta> element and includes the
       filename where the menu is defined.'''
    if 'content' not in elem.attrib:  # most likely stripped using strict
        return                       # security mode
    if page.is_local:
        local_path = os.path.split(page.url)[0]
        menu_file = os.path.join(local_path, elem.attrib["content"])
    elif page.is_remote:
        raise NotImplementedError
    else:
        local_path = os.path.split(page.url)[0][1:]
        menu_file = os.path.join(CrunchyPlugin.get_data_dir(),
                                 "server_root", local_path,
                                 elem.attrib["content"])
    menu, css = extract_menu(menu_file, page)
    if page.body:
        page.body.insert(0, menu)
    if css is not None:
        page.head.append(css)
    page.add_include("menu_included")

def insert_default_menu(page):
    """inserts the default Crunchy menu"""
    global _default_menu, _css
    if _default_menu is None:  # Note: for now we only assume we have
                              # one default menu (in English)
                              # This will need to be changed later.
        menu_file = os.path.join(CrunchyPlugin.get_data_dir(),
                                 "server_root", "menu_en.html")
        # we trust our own menus to be safe
        _default_menu, _css = extract_menu(menu_file, page, safe_menus=True)
    if page.body:
        page.body.insert(0, _default_menu) # make sure we insert at 0 i.e.
        # it appears first -
        # this is important for poorly formed tutorials (non-w3c compliant).
    try:
        page.head.append(_css)
    except Exception, info:
        print info
        print "_css=", _css
    # insert the required code to make the menu draggable
    if not page.includes("drag_included"):
        page.add_include("drag_included")
        page.insert_js_file("/drag.js")

def extract_menu(filename, page, safe_menus=False):
    '''extract a menu and css information from an html file.

       It assumes that the menu (usually an unordered list) is
       contained within the only <div> present in the file
       whereas the css information is contained in the single
       <link> in that file.'''
    try:
        tree = CrunchyPlugin.parse(filename)
    except Exception, info:
        print info
    # Treat menus just as suspiciously as the original file
    if not safe_menus:
        tree = security.remove_unwanted(tree, page)

    # extract menu for use in other files
    menu = tree.find(".//div")
    #head = tree.find("head")
    css = tree.find(".//link")

    # make the menu draggable
    menu.attrib['id'] = 'menu_box'
    menu.attrib['onmousedown'] = "dragStart(event, 'menu_box')"
    return menu, css

