'''
security_advisor.py

Inserts security information at the top of a page
'''

import src.CrunchyPlugin as cp
from src.security import set_page_security

provides = set(["/update"])

def register():
    cp.register_tag_handler("no_tag", "security", None, insert_security_info)
    cp.register_http_handler("/update%s"%cp.session_random_id, set_page_security)

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

    # let user security display level for a specific page
    if page.security_info[1] != 0:
        change_link = cp.SubElement(img, "a")
        change_link.attrib["href"] = 'javascript:allowSite()'
        change_link.text = "allow"

        page.add_js_code(update_security_js)

    if page.body:
        page.body.insert(0, outer_span)

update_security_js = """
function allowSite() {
    // parse out the URL from the querystring
    var queryString = window.location.href.substring((window.location.href.indexOf('?') + 1)).split('&');
    if (queryString[0].substring(0,4) != "url=") return;
    var hostname = unescape(queryString[0].substring(4));
    if (hostname.substring(0,7) != "http://") return;
    var endOfString = (hostname.indexOf("/", 7) == -1) ? hostname.length : hostname.indexOf("/", 7);
    hostname = hostname.substring(7,endOfString);

    if (confirm("Are you sure you wish to allow potentially dangerous content on this site?")) {
        var j = new XMLHttpRequest();
        j.open("POST", "/update%s?level=trusted", false);
        j.send(hostname);
        alert('Setting '+hostname+' to trusted');
        window.location.href = window.location.href;
    }
};
"""%cp.session_random_id