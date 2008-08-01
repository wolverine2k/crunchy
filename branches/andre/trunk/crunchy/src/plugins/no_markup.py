"""
no_markup.py:  no unit tests yet.

This plugin is used to process, according to the user's preference,
elements with no specific vlam.
"""

from src.interface import plugin, config

def register(): # tested
    '''registers a simple tag handler'''
    plugin['register_final_tag_handler']("pre", custom_vlam)

def custom_vlam(page, elem, uid): # tested
    '''
    inserts interactive elements in bare "pre" based on user's preferences.
    '''
    if config[page.username]['no_markup'] is not None:
        n_m = config[page.username]['no_markup'].lower()
        keyword = n_m.split(" ")[0]
        if "title" not in elem.attrib:
            elem.attrib["title"] = n_m
            page.handlers3["pre"]["title"][keyword](page, elem, uid)
    return