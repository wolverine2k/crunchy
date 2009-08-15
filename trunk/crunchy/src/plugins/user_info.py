'''
This module determines how to modify the display based on whether or not
a username/password has been set or not.
'''


from src.interface import plugin, accounts, Element, translate,\
    additional_menu_items
_ = translate['_']


def register(): # tested
    """
       registers the tag handlers for inserting menu as well as
       allowed positions for the menu.
    """
    plugin['register_begin_pagehandler'](insert_user_info)

def insert_user_info(page):
    '''determine what information to add based on the presence of not of
       user information.'''
    if not accounts:
        msg = _("""No user account has been set up: execution of Python code has
been disabled. Please use account_manager.py to create one or more user accounts.""")
        page.body.attrib['onload'] = "javascript:alert('%s')" % msg
