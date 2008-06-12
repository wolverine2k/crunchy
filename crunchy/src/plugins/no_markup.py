"""
no_markup.py:  no unit tests yet.

This plugin is used to process, according to the user's preference,
elements with no specific vlam.
"""

from src.interface import plugin, config

def register():
    '''registers a simple tag handler'''
    plugin['register_final_tag_handler']("pre", power_vlam)

def power_vlam(page, elem, uid):
    '''
    inserts interactive elements in bare "pre" based on user's preferences.
    '''
    n_m = config['no_markup'].lower()
    if n_m != 'none':
        keyword = n_m.split(" ")[0]
        if "title" not in elem.attrib:
            elem.attrib["title"] = n_m
            page.handlers3["pre"]["title"][keyword](page, elem, uid)
    return