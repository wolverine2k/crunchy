"""
This plugin is used to process, according to the user's preference,
elements with no specific vlam.
"""
import sys
from src.interface import plugin, config, u_print

def register(): # tested
    '''registers a simple tag handler'''
    plugin['register_final_tag_handler']("pre", custom_vlam)
    plugin['register_preprocess_page']("pre", modify_vlam)

def custom_vlam(page, elem, uid): # tested
    '''
    inserts interactive elements in bare "pre" based on user's preferences.
    '''
    if config[page.username]['no_markup'] is None:
        return
    n_m = config[page.username]['no_markup'] # allows only "keyword" i.e.
    keyword = n_m.split(" ")[0]
    if "title" not in elem.attrib:
        elem.attrib["title"] = n_m
        modify_vlam(page, elem, 'dummy') # this allows "fine tuning" of options
        page.handlers3["pre"]["title"][keyword](page, elem, uid)
    return

def modify_vlam(page, elem, dummy):
    '''modify the existing markup on a page.

    Restricted to changing title attribute values of an element.
    '''
    if config[page.username]['modify_markup'] is False:
        return
    if "title" not in elem.attrib:
        return
    for rule in config[page.username]['_modification_rules']:
        try:
            elem.attrib["title"] = dispatcher[rule[0]](elem.attrib["title"],
                                                                rule[1:])
        except e:
            u_print("Error found in user_markup.modify_vlam(): ", sys.exc_info()[1])
            u_print("rule = ", rule)
    return

def add_option(vlam, option): # tested
    '''adds an option to an existing markup'''
    return vlam + " " + option[0]

def remove_option(vlam, option): # tested
    '''removes an option, if present, from an existing markup'''
    return vlam.replace(option[0], '').strip()

def replace(vlam, values): # tested
    '''replace an option or keyword, if present, by a new value'''
    if values[0] in vlam:
        return vlam.replace(values[0], values[1])
    else:
        return vlam

dispatcher = {'add_option': add_option,
              'remove_option': remove_option,
              'replace': replace}