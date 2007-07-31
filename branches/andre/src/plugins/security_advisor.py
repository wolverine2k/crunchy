'''
security_advisor.py

Inserts security information at the top of a page
'''

import src.CrunchyPlugin as cp
def register():
    cp.register_tag_handler("no_tag", "security", None, insert_security_info)

def insert_security_info(page, *dummy):
    """Inserts security information at the top of a page"""
    if 'trusted' in page.security_info[0]:
        src = '/trusted.png'
    elif 'normal' in page.security_info[0]:
        src = '/normal.png'
    elif 'severe' in page.security_info[0]:
        src = '/severe.png'
    elif 'paranoid' in page.security_info[0]:
        src = '/paranoid.png'

    outer_span = cp.Element("span")
    outer_span.attrib["style"] = "top:10px; left:50px; font-size:10pt; position:absolute; z-index:2"
    level_img = cp.SubElement(outer_span, "img")
    level_img.attrib["src"] = src
    level_img.attrib["alt"] = "security level image"
    level_img.attrib["style"] = "border:0"
    level_img.tail = " "

    span = cp.SubElement(outer_span, "span")
    span.text = "[security level: " + page.security_info[0] + "] "
    img = cp.SubElement(span, "img")
    img.attrib["alt"] = "security result"
    if page.security_info[1] == 0:
        img.attrib["src"] = "/checkmark.png"
        img.tail = "No elements were removed"
    elif page.security_info[1] == 1:
        img.attrib["src"] = "/warning.png"
        img.tail = "One element was removed"
    else:
        img.attrib["src"] = "/warning.png"
        img.tail = "%d elements were removed"%page.security_info[1]

    if page.body:
        page.body.insert(0, outer_span)
