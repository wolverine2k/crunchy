'''
Username plugin.

Enable the insertion of a user's username anywhere in a page.
'''

from src.interface import plugin, Element, SubElement

def register():
    '''registers a simple tag handler'''
    plugin['register_tag_handler']("span", "title", "username", insert_username)

def insert_username(page, elem, dummy):
    '''Inserts the username, replacing the text previously used as a placeholder.'''
    elem.text = page.username