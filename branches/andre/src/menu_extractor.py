# Menu_extractor
# Extracts the standard crunchy menu and style file from a standard file
# so as to incorporate it into all pages displayed.

import os
from element_tree import HTMLTreeBuilder

styles = []
menu = None

def main(dir):
    global menu, styles
    filename = os.path.normpath(os.path.join(dir, "index.html"))
    try:
        tree = HTMLTreeBuilder.parse(filename)
    except Exception, info:
        print info
    head = tree.find("head")
    body = tree.find("body")
    menu = body.find(".//div")
    for link in head.findall('.//link'):
        styles.append(link)
    body.clear()
    head.clear()
    body.insert(0, menu)
    for link in styles:
        head.insert(0, link)
    return
