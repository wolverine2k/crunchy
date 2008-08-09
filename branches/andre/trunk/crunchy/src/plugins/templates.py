'''
Page template plugin

'''

import copy
import os
from src.vlam import BasePage

_templates = {}

from src.interface import config, plugin, Element, tostring

def register():
    '''registers a simple tag handler'''
    plugin['register_tag_handler']("meta", "title", "template",
                                                    merge_with_template)

def create_template(name, username, filehandle): # tested
    '''creates a page template from a file object'''
    template = BasePage(username)
    template.create_tree(filehandle)
    template.find_head()
    template.find_body()
    _templates[name] = template
    return

def merge_with_template(page, elem, dummy):
    '''merge an html file with a template'''
    content_div = find_content_div(page)
    if content_div is None:
        print "div with id=content not found; will not merge with template."
        return
    if page.url.startswith('http'):
        print "Merging with remote templates not implemented yet."
        return
    url = elem.attrib['title'].split(' ')[1]
    base_dir, dummy = os.path.split(page.url)
    url = os.path.normpath(os.path.join(config['crunchy_base_dir'], "server_root",
                                        base_dir[1:], url))
    if url not in _templates:
        try:
            filehandle = open(url)
        except:
            print "In merge_with_template, can not open url =", url
            return
        create_template(url, page.username, filehandle)
    template = _templates[url]
    template_content_div = find_content_div(template)
    if template_content_div is None:
        print "Invalid template file: div with id=content not found."
        return
    new_head = merge_elements(template.head, page.head)
    page.head.clear()
    page.head[:] = [new_head]
    page.body.clear()

   # see if we need to replace title_bar div

    page.body[:] = [template.body]
    template_content_div.clear()
    template_content_div[:] = [content_div]
    return

def find_content_div(page):
    '''finds a div with id=content on a given page'''
    found_div = False
    content_div = None
    for div in page.tree.findall(".//div"):
        if 'id' in div.attrib:
            if div.attrib['id'] == 'content':
                found_div = True
                content_div = div
                break
    return content_div


def merge_elements(main, secondary):
    '''makes a copy of the main element, and merge all the subelements of
    the secondary.'''
    new_main = copy.deepcopy(main)
    for elem in secondary:
        new_main.append(elem)
    return new_main

def remove_subelement(main, sub_element):
    '''makes a copy of the main element, and remove the listed subelement.'''
    new_main = copy.deepcopy(main)
    found = new_main.find(".//%s" % sub_element)
    try:
        new_main.remove(found)
    except:
        print "can't remove element ", found
        print "Most likely, it is not a direct child of the main element."
    return new_main