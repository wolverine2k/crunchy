'''
Page template plugin.

Enable the use of a template for tutorial pages.
'''
import codecs
import copy
import os
import traceback
from src.vlam import BasePage

_templates = {}

from src.interface import config, plugin, u_print

def register():
    '''registers a simple tag handler'''
    plugin['register_meta_handler']("title", merge_with_template)

def create_template(name, username, filehandle): # tested
    '''creates a page template from a file object'''
    template = BasePage(username)
    template.create_tree(filehandle)
    template.find_head()
    template.find_body()
    _templates[name] = template
    # transform template title into harmless empty style so that the correct
    # title is displayed in the browser tab.
    template_title = template.tree.find(".//title")
    template_title.clear()
    template_title.text = ''
    template_title.tail = ''
    template_title.tag = 'style'
    return

def return_template(page, elem):
    '''determine the file to use as a template and if a new template needs
       to be created.'''
    url = elem.attrib['title'].strip().split(' ')[-1]
    base_dir, dummy = os.path.split(page.url)
    if page.is_from_root:
        url = os.path.normpath(os.path.join(config['crunchy_base_dir'], "server_root",
                                        base_dir[1:], url))
    elif page.is_local:
        url = os.path.normpath(os.path.join(base_dir, url))
    if url not in _templates:
        try:
            filehandle = codecs.open(url, encoding='utf8')
        except:
            u_print("In merge_with_template, can not open url =", url)
            traceback.print_exc()
            return None
        create_template(url, page.username, filehandle)
    return _templates[url]

def merge_with_template(page, elem):
    '''merge an html file with a template'''
    if 'template' not in elem.attrib['title']:
        return
    # The format we expect is
    # <meta title="template template_file.html">
    # However, for reStructuredText files, we have instead the following:
    # <meta title="template" content="template_file.html">
    # So, let's convert to the canonical form if possible.
    if elem.attrib['title'] == 'template':
        if 'content' not in elem.attrib:
            return
        elem.attrib['title'] += " " + elem.attrib['content']

    page_divs = find_divs(page)
    if not page_divs:
        u_print("No div found in page; can not merge with template.")
        return
    if page.url.startswith('http'):
        u_print("Merging with remote templates not implemented yet.")
        return

    template = return_template(page, elem)
    if template is None:
        return
    merge_heads(template, page)
    merge_bodies(template, page, page_divs)
    return

def find_divs(page): # tested
    '''find all divs with id attributes and return them in a dict'''
    divs = {}
    for div in page.tree.findall(".//div"):
        if 'id' in div.attrib:
            divs[div.attrib['id']] = div
    return divs

def merge_heads(template, page): # tested
    '''merge the <head>s of the template with that of the
       page being processed.'''
    new_head = merge_elements(template.head, page.head)
    page.head.clear()
    page.head[:] = new_head
    return

def merge_elements(main, secondary): # tested
    '''makes a copy of the main element, and merge all the subelements of
    the secondary element.'''
    new_main = copy.deepcopy(main)
    for elem in secondary:
        new_main.append(elem)
    return new_main

def merge_bodies(template, page, page_divs):
    '''using the template's <body> as the new body, selectively the template's
       <div>s by the page's <div>s.'''
    page.body.clear()
    page.body[:] = [copy.deepcopy(template.body)]
    # to ensure that nested divs are replaced properly, we need to replace
    # them in the order in which they appear in the page
    for div in page.body.findall(".//div"):
        if 'id' in div.attrib:
            if div.attrib['id'] in page_divs:
                _id = div.attrib['id']
                div.clear()
                div.attrib['id'] = _id
                div[:] = page_divs[_id]
                div.text = page_divs[_id].text
                div.tail = page_divs[_id].tail
