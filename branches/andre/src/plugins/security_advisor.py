'''
security_advisor.py

Inserts security information at the top of a page
'''
import random
from urlparse import urlsplit

import src.configuration as configuration
import src.CrunchyPlugin as cp
_ = cp._

provides = set(["/allow_site", "/enter_key", "/set_trusted"])

def register():
    cp.register_tag_handler("no_tag", "security", None, insert_security_info)
    cp.register_http_handler("/allow_site", allow_site)
    cp.register_http_handler("/enter_key", enter_trusted_key)
    cp.register_http_handler("/set_trusted", set_security_list)

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
    outer_span.attrib["class"] = "security_info"
    outer_span.text = _("Crunchy security level: [") +\
                        page.security_info['level'] + "]"
    level_img = cp.SubElement(outer_span, "img")
    level_img.attrib["src"] = src
    level_img.attrib["alt"] = "security level image"
    level_img.attrib["style"] = "border:0;height:20px"
    level_img.tail = " "

    span = cp.SubElement(outer_span, "span")
    span.text = _(" - Page content:")
    img = cp.SubElement(span, "img")
    img.attrib["alt"] = "security result"
    img.attrib["style"] = "border:0;height:20px"
    if page.security_info['number removed'] == 0:
        img.attrib["src"] = "/ok.png"
        img.tail = _("No elements were removed. ")
    elif page.security_info['number removed'] == 1:
        img.attrib["src"] = "/warning.png"
        img.tail = _("One element was removed. - ")
    else:
        img.attrib["src"] = "/warning.png"
        img.tail = _("%d elements were removed. - ")%page.security_info['number removed']
    if page.security_info['number removed'] != 0:
        span.tail = " "
        view = cp.SubElement(outer_span, "a")
        view.attrib["onclick"] = "show_security_info();"
        view.attrib["href"] = "#"
        view.attrib['style'] = "text-decoration: underline;"
        view.text = _(" View security report ")
    page.body.insert(0, outer_span)

    # Next, the hidden container for the full security information

    if not page.includes("security_included"):
        page.add_include("security_included")
        page.insert_js_file("/security.js")

        info_container = cp.Element("div")
        info_container.attrib["id"] = "security_info"
        format_report(page, info_container)

        # prompt user to approve sites as soon as the second page is loading
        if page.url != "/index.html" and configuration.defaults.site_security \
              and not configuration.initial_security_set:
            configuration.initial_security_set = True
            page.add_css_code(security_css%('block','block'))
            directions = cp.SubElement(info_container, "h4")
            directions.text = _("Before browsing any further ...\n\n")
            directions.text += _("Do you wish to retain the existing settings for these sites?\n\n")
            directions.text += _("You can change any of them before clicking on the approve button.\n\n")

            # in case list gets too long, we include buttons at top and bottom
            approve_btn = cp.SubElement(info_container, "button")
            site_num = len(configuration.defaults.site_security)
            approve_btn.attrib["onclick"] = "app_approve('%d')"%site_num
            approve_btn.text = _("Approve")
            cp.SubElement(info_container, "span").text = " "
            deny_btn = cp.SubElement(info_container, "button")
            deny_btn.attrib["onclick"] = "app_remove_all()"
            deny_btn.text = _("Remove all")

            site_num = 0
            options = [['trusted', 'trusted'],
                        ['normal', 'normal'],
                        ['strict', 'strict'],
                        ['display trusted', 'display trusted'],
                        ['display normal', 'display normal'],
                        ['display strict', 'display strict'],
                        ['remove', _('remove from list')]]
            for site in configuration.defaults.site_security:
                site_num += 1
                fieldset = cp.SubElement(info_container, "fieldset")
                site_label = cp.SubElement(fieldset, "legend")
                site_label.text = site
                form = cp.SubElement(fieldset, "form")
                form.attrib['id'] = "site_" + str(site_num)
                form.attrib['name'] = site
                for option in options:
                    inp = cp.SubElement(form, 'input')
                    inp.attrib['value'] = option[0]
                    inp.attrib['type'] = 'radio'
                    inp.attrib['name'] = "rad"
                    inp.text = option[1]
                    if option[1] == configuration.defaults.site_security[site]:
                        inp.attrib['checked'] = 'checked'
            # in case list gets too long, we include buttons at top and bottom
            approve_btn = cp.SubElement(info_container, "button")
            approve_btn.attrib["onclick"] = "app_approve('%d')"%site_num
            approve_btn.text = _("Approve")
            cp.SubElement(info_container, "span").text = " "
            deny_btn = cp.SubElement(info_container, "button")
            deny_btn.attrib["onclick"] = "app_remove_all()"
            deny_btn.text = _("Remove all")
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
    global netloc
    if page.security_info['tags removed']:
        h2 = cp.SubElement(div, 'h2')
        h2.text = _('Removed: tag not allowed')

        table = cp.SubElement(div, 'table')
        table.attrib['class'] = 'summary'
        tr = cp.SubElement(table, 'tr')
        th = cp.SubElement(tr, 'th')
        th.text = _('Tag removed')
        th = cp.SubElement(tr, 'th')
        th.text = _('Number of times')

        for item in page.security_info['tags removed']:
            tr = cp.SubElement(table, 'tr')
            td = cp.SubElement(tr, 'td')
            td.text = item[0]
            td = cp.SubElement(tr, 'td')
            td.text = str(item[1])

    if page.security_info['attributes removed']:
        h2 = cp.SubElement(div, 'h2')
        h2.text = _('Removed: attribute, or attribute value not allowed')

        table = cp.SubElement(div, 'table')
        table.attrib['class'] = 'summary'

        tr = cp.SubElement(table, 'tr')
        th = cp.SubElement(tr, 'th')
        th.text = _('Tag')
        th = cp.SubElement(tr, 'th')
        th.text = _('Attribute')
        th = cp.SubElement(tr, 'th')
        th.text = _('Value (if relevant)')

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
        h2.text = _('Removed: style tag or attribute not allowed')

        table = cp.SubElement(div, 'table')
        table.attrib['class'] = 'summary'

        tr = cp.SubElement(table, 'tr')
        th = cp.SubElement(tr, 'th')
        th.text = _('Tag')
        th = cp.SubElement(tr, 'th')
        th.text = _('Attribute (if relevant)')
        th = cp.SubElement(tr, 'th')
        th.text = _('Value')

        for item in page.security_info['styles removed']:
            tr = cp.SubElement(table, 'tr')
            td = cp.SubElement(tr, 'td')
            td.text = item[0]
            td = cp.SubElement(tr, 'td')
            td.text = item[1]
            td = cp.SubElement(tr, 'td')
            td.text = item[2]

    netloc = urlsplit(page.url).netloc #l ocalhost will return empty string
    if page.security_info['number removed'] != 0 and netloc:
        site_num = 1
        options = [['trusted', 'trusted'],
                    ['normal', 'normal'],
                    ['strict', 'strict'],
                    ['display trusted', 'display trusted'],
                    ['display normal', 'display normal'],
                    ['display strict', 'display strict'],
                    ['remove', _('remove from list')]]

        fieldset = cp.SubElement(div, "fieldset")
        site_label = cp.SubElement(fieldset, "legend")
        site_label.text = netloc
        form = cp.SubElement(fieldset, "form")
        form.attrib['id'] = "single_site_" + str(site_num)
        form.attrib['name'] = netloc
        for option in options:
            inp = cp.SubElement(form, 'input')
            inp.attrib['value'] = option[0]
            inp.attrib['type'] = 'radio'
            inp.attrib['name'] = "rad"
            inp.text = option[1]
            if netloc in configuration.defaults.site_security:
                if option[1] == configuration.defaults.site_security[netloc]:
                    inp.attrib['checked'] = 'checked'
        approve_btn = cp.SubElement(div, "button")
        approve_btn.attrib["onclick"] = "javascript:allow_site();"
        approve_btn.text = _("Select site security level")
    return

def allow_site(request):
    '''function used to have the user confirm the security level
       for the site'''
    global trusted_key, netloc

    if request.data == "":
        request.send_response(200)
        request.end_headers()
        request.wfile.write("asdf")
        request.wfile.flush()
        return

    # create random site key or users to enter (not too long)
    n = int(random.random()*1000000)
    if n < 100000:
        n = 999999 - n
    trusted_key = str(n)

    # print a trusted site key in the console
    print "----------------------------------------------------"
    print _("Host: ") + netloc
    print _("Confirmation code: ") + trusted_key
    print "----------------------------------------------------"

    request.send_response(200)
    request.end_headers()
    request.wfile.flush()

# have the users enter a trusted site key to add the site to a list
def enter_trusted_key(request):
    global trusted_key, netloc
    user_key = request.data

    if user_key == trusted_key:
        request.send_response(200)
        request.end_headers()
        request.wfile.write("Success")
        request.wfile.flush()
    else:
        request.send_response(200)
        request.end_headers()
        request.wfile.write("Failed")
        request.wfile.flush()

def set_security_list(request):
    site_list_info = request.data.strip(',').split(',')
    site_list = []
    for site_info in site_list_info:
        if ":" not in site_info:
            continue
        site = site_info.split(':')
        mode = site[1].strip()
        site = site[0].strip()
        site_list.append(site)
        if site.strip() != '':
            if mode in ['trusted', 'normal', 'strict',
               'display normal', 'display strict', 'display trusted']:
                configuration.defaults.site_security[site] = mode
                if cp.DEBUG:
                    print '%s has been set to %s: '%(site, mode)
            else:
                del configuration.defaults.site_security[site]
    # removing items in dict is done in two steps: can't loop over
    # dict while its size changes
    to_be_deleted = []
    for site in configuration.defaults.site_security:
        if site not in site_list:
            to_be_deleted.append(site)
    for site in to_be_deleted:
        del configuration.defaults.site_security[site]
    request.send_response(200)
    request.end_headers()
    request.wfile.write("")
    request.wfile.flush()

security_css = """
#security_info {
    position: fixed;
    top: 60px;
    right: 100px;
    height: 85%%;
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
    right: 110px;
    color: #fe0;
    background-color: #369;
    font: 14pt sans-serif;
    cursor: pointer;
    padding: 4px 4px 0 4px;
    display: %s;  /* will appear only when needed */
    z-index:12;
}
"""
