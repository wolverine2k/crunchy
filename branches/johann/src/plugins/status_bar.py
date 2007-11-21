"""
Status bar plugin, unifies the old menu and security plugins
"""
import os
import src.CrunchyPlugin as CrunchyPlugin
import src.security as security
import src.configuration as configuration
_default_menu = None
_css = None

def register():
    """The register() function is required for all plugins."""
    #CrunchyPlugin.register_tag_handler("meta", "name", "crunchy_menu", insert_special_menu)
    #CrunchyPlugin.register_tag_handler("no_tag", "menu", None, insert_default_menu)
    CrunchyPlugin.register_tag_handler("no_tag", "insert_status_bar", None, insert_status_bar)

def insert_status_bar(page):
    if page.body:
        bar = CrunchyPlugin.Element("div")
        bar.text = "Experimental Status Bar: "
        bar.attrib["id"] = "crunchy_status"
        link = CrunchyPlugin.SubElement(bar, "a")
        link.attrib["href"] = "/"
        link.text = "Crunchy Home"
        link = CrunchyPlugin.SubElement(bar, "a")
        link.attrib["href"] = "/"
        link.text = "Quit Crunchy"
        page.body.insert(0, bar)