'''
security_advisor.py

Inserts security information at the top of a page
'''

from src.security import get_site_security,set_site_security,propose_trusted,site_access
import src.CrunchyPlugin as cp
import random

provides = set(["/allow_site", "/enter_key", "/set_trusted"])

def register():
    cp.register_tag_handler("no_tag", "security", None, insert_security_info)
    cp.register_http_handler("/allow_site%s"%cp.session_random_id, allow_site)
    cp.register_http_handler("/enter_key%s"%cp.session_random_id, enter_trusted_key)
    cp.register_http_handler("/set_trusted%s"%cp.session_random_id, set_list_trusted)

def insert_security_info(page, *dummy):
    """Inserts security information at the top of a page"""
    if not page.body:
        return

    #===First, the static display at the top

    if 'trusted' in page.security_info['level']:
        src = '/trusted.png'
    elif 'normal' in page.security_info['level']:
        src = '/severe.png'
    elif 'strict' in page.security_info['level']:
        src = '/paranoid.png'

    outer_span = cp.Element("span")
    outer_span.attrib["style"] = "top:10px; left:50px; font-size:10pt; position:absolute; z-index:2"
    outer_span.text = "Crunchy security level: "
    level_img = cp.SubElement(outer_span, "img")
    level_img.attrib["src"] = src
    level_img.attrib["alt"] = "security level image"
    level_img.attrib["style"] = "border:0"
    level_img.attrib["height"] = "20"
    level_img.tail = " "

    span = cp.SubElement(outer_span, "span")
    span.text = "[" + page.security_info['level'] + "] Page content:"
    img = cp.SubElement(span, "img")
    img.attrib["alt"] = "security result"
    if page.security_info['number removed'] == 0:
        img.attrib["src"] = "/ok.png"
        img.tail = "No elements were removed"
    elif page.security_info['number removed'] == 1:
        img.attrib["src"] = "/warning.png"
        img.tail = "One element was removed"
    else:
        img.attrib["src"] = "/warning.png"
        img.tail = "%d elements were removed"%page.security_info['number removed']
    if page.security_info['number removed'] != 0:
        span.tail = " "
        view = cp.SubElement(outer_span, "a")
        view.attrib["onclick"] = "show_security_info();"
        view.attrib["href"] = "#"
        view.text = "View security report"
    page.body.insert(0, outer_span)

    # Next, the hidden container for the full security information

    if not page.includes("security_included"):
        page.add_include("security_included")
        page.insert_js_file("/security.js")

        info_container = cp.Element("div")
        info_container.attrib["id"] = "security_info"
        format_report(page, info_container)
        #info_container.text = "Here's the information\n more information "

        # read list of proposed trusted sites
        try:
            proposed = open('proposed.txt')
            approve_list = proposed.readlines()
            proposed.close()
        except:
            approve_list = []

        # prompt user to approve sites on index.html only
        if page.url == "/index.html" and len(approve_list) > 0:
            page.add_css_code(security_css%('block','block'))
            directions = cp.SubElement(info_container, "p")
            directions.text = "Do you wish to allow the following websites to be trusted?\n\n"
            directions.text += "If you did not approve these sites, click Deny All"

            site_num = 1
            for site in approve_list:
                site = site.strip()
                site_label = cp.SubElement(info_container, "label")
                site_label.attrib["for"] = "site_"+str(site_num)

                site_cb = cp.SubElement(site_label, "input")
                site_cb.attrib["id"] = "site_"+str(site_num)
                site_cb.attrib["value"] = site
                site_cb.text = " " + site + "\n"
                site_cb.attrib["type"] = "checkbox"
                site_num += 1

            select_text = cp.SubElement(info_container, "p")
            select_text.text = "Select: "
            select_btn = cp.SubElement(select_text, "a")
            select_btn.attrib["href"] = 'javascript:app_select_all()'
            select_btn.text = "All"
            cp.SubElement(select_text, "span").text = ", "

            select_btn = cp.SubElement(select_text, "a")
            select_btn.attrib["href"] = 'javascript:app_select_none()'
            select_btn.text = "None"

            approve_btn = cp.SubElement(info_container, "button")
            approve_btn.attrib["onclick"] = 'app_approve()'
            approve_btn.text = "Approve"
            cp.SubElement(info_container, "span").text = " "
            deny_btn = cp.SubElement(info_container, "button")
            deny_btn.attrib["onclick"] = 'app_deny_all()'
            deny_btn.text = "Deny All"

        else:
            page.add_css_code(security_css%('none','none'))

        page.body.append(info_container)

        info_container_x = cp.Element("div")
        info_container_x.attrib["id"] = "security_info_x"
        info_container_x.attrib["onclick"] = "hide_security_info()"
        info_container_x.text = "X"
        page.body.append(info_container_x)

def format_report(page, div):
    '''puts the security information (extracted material) into a table
       for display'''
    if page.security_info['tags removed']:
        h2 = cp.SubElement(div, 'h2')
        h2.text = 'Removed: tag not allowed'

        table = cp.SubElement(div, 'table')
        table.attrib['class'] = 'summary'
        tr = cp.SubElement(table, 'tr')
        th = cp.SubElement(tr, 'th')
        th.text = 'Tag removed'
        th = cp.SubElement(tr, 'th')
        th.text = 'Number of times'

        for item in page.security_info['tags removed']:
            tr = cp.SubElement(table, 'tr')
            td = cp.SubElement(tr, 'td')
            td.text = item[0]
            td = cp.SubElement(tr, 'td')
            td.text = str(item[1])

    if page.security_info['attributes removed']:
        h2 = cp.SubElement(div, 'h2')
        h2.text = 'Removed: attribute, or attribute value not allowed'

        table = cp.SubElement(div, 'table')
        table.attrib['class'] = 'summary'

        tr = cp.SubElement(table, 'tr')
        th = cp.SubElement(tr, 'th')
        th.text = 'Tag'
        th = cp.SubElement(tr, 'th')
        th.text = 'Attribute'
        th = cp.SubElement(tr, 'th')
        th.text = 'Value (if relevant)'

        for item in page.security_info['attributes removed']:
            tr = cp.SubElement(table, 'tr')
            td = cp.SubElement(tr, 'td')
            td.text = item[0]
            td = cp.SubElement(tr, 'td')
            td.text = item[1]
            td = cp.SubElement(tr, 'td')
            td.text = item[2]

    if page.security_info['styles removed']:
        h2 = cp.SubElement(div, 'h2')
        h2.text = 'Removed: style tag or attribute not allowed'

        table = cp.SubElement(div, 'table')
        table.attrib['class'] = 'summary'

        tr = cp.SubElement(table, 'tr')
        th = cp.SubElement(tr, 'th')
        th.text = 'Tag'
        th = cp.SubElement(tr, 'th')
        th.text = 'Attribute (if relevant)'
        th = cp.SubElement(tr, 'th')
        th.text = 'Value'

        for item in page.security_info['styles removed']:
            tr = cp.SubElement(table, 'tr')
            td = cp.SubElement(tr, 'td')
            td.text = item[0]
            td = cp.SubElement(tr, 'td')
            td.text = item[1]
            td = cp.SubElement(tr, 'td')
            td.text = item[2]

    if page.security_info['number removed'] != 0 and get_site_security(page.url) != 'trusted':
        page.add_js_code(allow_site_js)

        br = cp.SubElement(div, "br")
        change_link = cp.SubElement(br, "a")
        change_link.attrib["href"] = 'javascript:allow_site()'
        change_link.text = "Allow site"

    return

"""Set site to trusted
This is called when the user allows a site from the security report
"""
def allow_site(request):

    # checks if site key was already printed
    # TODO: warn user if site access level is already set
    if request.data == "" or request.data in propose_trusted.values():
        request.send_response(200)
        request.end_headers()
        request.wfile.write("asdf")
        request.wfile.flush()

        return

    # create random site key or users to enter (not too long)
    trusted_key = str(int(random.random()*1000)) + str(int(random.random()*1000))

    # print a trusted site key in the console
    print "----------------------------------------------------"
    print "Host: " + request.data
    print "Trusted site key: " + trusted_key
    print "----------------------------------------------------"

    propose_trusted[trusted_key] = request.data

    request.send_response(200)
    request.end_headers()
    request.wfile.flush()

# have the users enter a trusted site key to add the site to a list
def enter_trusted_key(request):
    trusted_key = request.data

    # trusted key was correct
    if trusted_key in propose_trusted.keys():
        proposed = open("proposed.txt", 'a')
        proposed.write(propose_trusted[trusted_key] + "\n")
        proposed.close()

        request.send_response(200)
        request.end_headers()
        request.wfile.write("Success")
        request.wfile.flush()

    else:
        request.send_response(200)
        request.end_headers()
        request.wfile.write("Failed")
        request.wfile.flush()

def set_list_trusted(request):

    site_list = request.data.strip(',').split(',')

    for site in site_list:
        set_site_security(site, 'trusted')
        if cp.DEBUG:
            print 'Site has been set to trusted: ' + site

    # clear proposed list
    sites = open("proposed.txt", 'w')
    sites.close()

    # save trusted sites
    sites = open("trusted.txt", 'w')
    sites.write('\n'.join(site_access['trusted']))
    sites.close()
    if cp.DEBUG:
        print 'Saving trusted sites: ' + '|'.join(site_access['trusted'])

    request.send_response(200)
    request.end_headers()
    request.wfile.write("")
    request.wfile.flush()

security_css = """
#security_info {
    position: fixed;
    top: 60px;
    right: 400px;
    width: 50%%;
    height: 75%%;
    overflow:auto;
    border: 4px outset #369;
    color: black;
    background-color: white;
    font: 10pt monospace;
    margin: 0;
    padding: 4px;
    padding-right: 30px;
    white-space: -moz-pre-wrap; /* Mozilla, supported since 1999 */
    white-space: -pre-wrap; /* Opera 4 - 6 */
    white-space: -o-pre-wrap; /* Opera 7 */
    white-space: pre-wrap; /* CSS3 - Text module (Candidate Recommendation)
                            http://www.w3.org/TR/css3-text/#white-space */
    word-wrap: break-word; /* IE 5.5+ */
    display: %s;  /* will appear only when needed */
    z-index:11;
}
#security_info_x {
    position: fixed;
    top: 65px;
    right: 410px;
    color: #fe0;
    background-color: #369;
    font: 14pt sans-serif;
    cursor: pointer;
    padding: 4px 4px 0 4px;
    display: %s;  /* will appear only when needed */
    z-index:12;
}
"""

allow_site_js = """
// allow site code will go here
"""
