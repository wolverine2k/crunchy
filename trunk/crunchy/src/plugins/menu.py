"""  Menu plugin.

Other than through a language preference, Crunchy menus can be modified
by tutorial writers using a custom meta declaration.
"""

import os

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, parse, Element, config
import src.security as security

current_language = None

def register():
    """
       registers two tag handlers for inserting custom menus
    """
    plugin['register_tag_handler']("meta", "name", "crunchy_menu", insert_special_menu)
    plugin['register_tag_handler']("no_tag", "menu", None, insert_default_menu)

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
        menu_file = os.path.join(plugin['get_root_dir'](), "server_root",
                                       local_path, elem.attrib["content"])
    menu, css = extract_menu(menu_file, page)
    if page.body:
        page.body.insert(0, menu)
        activate_security_info(page, menu)
    if css is not None:
        page.head.append(css)
    page.add_include("menu_included")

def insert_default_menu(page):
    """inserts the default Crunchy menu"""
    global current_language, _default_menu, _css
    if config['language'] != current_language:
        _default_menu, _css = select_language(config['language'])
    activate_security_info(page, _default_menu)
    if page.body:
        page.body.insert(0, _default_menu) # make sure we insert at 0 i.e.
        # it appears first -
        # this is important for poorly formed tutorials (non-w3c compliant).
    try:
        page.head.append(_css)
    except Exception:#, info:
        print("Cannot append css code in the head") # info
        print("_css= " + _css)

def activate_security_info(page, menu):
    '''
    Insert javascript call in link so that the security report is displayed,
    as well as image showing security status.
    '''
    # First, add javascript code to display security report.
    # While one can include such a link in the standard menu file included
    # in the Crunchy distribution, custom menus would have such call
    # removed for security reasons.
    for elem in menu.getiterator('a'):
        if 'id' in elem.attrib:
            if elem.attrib['id'] == "security_info_link":
                elem.attrib['onclick'] = "show_security_info();"
                break

    # Second, include image to indicate security status
    image_found = False
    # First, attempt to update the image identifying the security result
    for elem in menu.getiterator('img'):
        if 'id' in elem.attrib:
            if elem.attrib['id'] == "security_result_image":
                elem.attrib['src'] = page.security_result_image
                image_found = True
                break
    # otherwise, add the image in the first place
    if not image_found:
        for elem in menu.getiterator('a'):
            if 'id' in elem.attrib:
                if elem.attrib['id'] == "security_info_link":
                    img = Element('img')
                    img.attrib['src'] = page.security_result_image
                    img.attrib['id'] = "security_result_image"
                    elem.attrib['title'] = 'crunchy_leave_alone'
                    elem.append(img)
                    break
    return

def extract_menu(filename, page, safe_menus=False):
    '''extract a menu and css information from an html file.

       It assumes that the menu is contained within the first <div> found in
       the file whereas the css information is contained in the first
       <link> in that file.'''
    try:
        tree = parse(filename)
    except Exception:#, info:
        print("cannot create a tree from the file")# info
    # Treat menus just as suspiciously as other files
    if not safe_menus:
        tree = security.remove_unwanted(tree, page)
    # extract menu for use in other files
    menu = tree.find(".//div")
    css = tree.find(".//link")
    return menu, css

def select_language(lang):
    '''
    Select a default menu based on a language choice. If the menu for the
    chosen language can not be found, an English menu is selected instead.
    '''
    global current_language
    menu_file = os.path.join(plugin['get_root_dir'](), "server_root",
                                 lang, "menu.html")
    if os.path.exists(menu_file):
        current_language = config['language']
    else:
        menu_file = os.path.join(plugin['get_root_dir'](), "server_root",
                                 "en", "menu.html")
        if current_language == None:
            current_language = 'en'
    # default menus, provided by Crunchy developers, are assumed to be safe.
    return extract_menu(menu_file, "dummy", safe_menus=True)
