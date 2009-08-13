'''
Username plugin.

Enable the insertion of a user's username anywhere in a page.
'''

from src.interface import plugin, Element, SubElement

def register():
    '''registers a simple tag handler'''
    plugin['register_tag_handler']("span", "title", "username", insert_username)

def insert_username(page, elem, dummy):
    '''When used in server/secure mode, inserts the username,
       replacing the text previously used as a placeholder - otherwise,
       inserts the name as a link to an explanation regarding the risks
       of running Crunchy in single (unsecure) user mode.'''
    if page.username == "Security Risk":
        im = SubElement(elem, "img", src="/images/stop.png")
        a = SubElement(elem, "a", href="/docs/about/magic.html")
        a.text = "Security Risk"
        im = SubElement(elem, "img", src="/images/stop.png")
    else:
        elem.text = page.username