'''
security_advisor.py

Inserts security information at the top of a page
'''
import random
from urlparse import urlsplit

import src.configuration as configuration
import src.CrunchyPlugin as cp
_ = cp._

provides = set(["/allow_site", "/enter_key", "/set_trusted", "/remove_all"])

def register():
    cp.register_tag_handler("no_tag", "security", None, insert_security_info)
##    cp.register_http_handler("/allow_site", allow_site)
##    cp.register_http_handler("/enter_key", enter_trusted_key)
    cp.register_http_handler("/set_trusted", set_security_list)
    cp.register_http_handler("/remove_all", empty_security_list)

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

    span = cp.Element("span")
    span.attrib['class'] = "security_report" # in file menu_basic.css
    level_img = cp.SubElement(span, "img")
    level_img.attrib["src"] = src
    level_img.attrib["alt"] = "security level image"
    level_img.attrib["style"] = "border:0;height:12pt"
    level_img.tail = _(" Crunchy security level: ") +\
                        page.security_info['level']

    br = cp.SubElement(span, "br")

    img = cp.SubElement(span, "img")
    img.attrib["alt"] = "security result"
    img.attrib["style"] = "border:0;height:12pt"
    if page.security_info['number removed'] == 0:
        img.attrib["src"] = "/ok.png"
        img.tail = _(" No elements were removed. ")
    elif page.security_info['number removed'] == 1:
        img.attrib["src"] = "/warning.png"
        img.tail = _(" One element was removed. - ")
    else:
        img.attrib["src"] = "/warning.png"
        img.tail = _(" %d elements were removed. - ")%page.security_info['number removed']
    if not page.url.startswith("/"):
        view = cp.SubElement(span, "a")
        view.attrib["onclick"] = "show_security_info();"
        view.attrib["href"] = "#"
        view.attrib['style'] = "text-decoration: underline;"
        view.text = _(" View report ")
    page.body.insert(0, span)

    # Next, the hidden container for the full security information

    if not page.includes("security_included"):
        page.add_include("security_included")
        page.insert_js_file("/security.js")

        info_container = cp.Element("div")
        info_container.attrib["id"] = "security_info"
        format_report(page, info_container)

        # prompt user to approve sites as soon as the first page is loaded
        # if there are sites for which to confirm the security level.
        if (page.url.startswith("/index")
                  # will work with /index_fr.html ...
              and configuration.defaults.site_security
                  # something to confirm
              and not configuration.initial_security_set):
                  # only do it once per session
            configuration.initial_security_set = True
            page.add_css_code(security_css%('block','block'))
            h2 = cp.SubElement(info_container, 'h2')
            h2.text = _('Confirm the security levels')
            h2.attrib['class'] = "crunchy"
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
                    label = cp.SubElement(form, 'label')
                    label.text = option[1]
                    label.attrib['for'] = site + option[0]
                    inp = cp.SubElement(label, 'input')
                    inp.attrib['value'] = option[0]
                    inp.attrib['type'] = 'radio'
                    inp.attrib['name'] = "rad"
                    inp.attrib['id'] = site + option[0]
                    br = cp.SubElement(form, 'br')
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
        h2.attrib['class'] = "crunchy"

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
        h2.attrib['class'] = "crunchy"

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
        h2.attrib['class'] = "crunchy"

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

    netloc = urlsplit(page.url).netloc # localhost will return empty string
    if page.security_info['number removed'] != 0 and netloc:
        h2 = cp.SubElement(div, 'h2')
        h2.text = _('You may select a site specific security level:')
        h2.attrib['class'] = "crunchy"
        if netloc in configuration.defaults.site_security:
            p = cp.SubElement(div, 'p')
            p.text = _("If you want to preserve the existing selection, ")
            p.text += _("simply dismiss this window by clicking on the X above.")
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
            label = cp.SubElement(form, 'label')
            label.text = option[1]
            label.attrib['for'] = netloc + option[0]
            inp = cp.SubElement(label, 'input')
            inp.attrib['value'] = option[0]
            inp.attrib['type'] = 'radio'
            inp.attrib['name'] = "rad"
            inp.attrib['id'] = netloc + option[0]
            br = cp.SubElement(form, 'br')
            if netloc in configuration.defaults.site_security:
                if option[1] == configuration.defaults.site_security[netloc]:
                    inp.attrib['checked'] = 'checked'
        approve_btn = cp.SubElement(div, "button")
        approve_btn.attrib["onclick"] = "javascript:allow_site();"
        approve_btn.text = _("Select site security level")

        p = cp.SubElement(div, 'p')
        p.text = _("""
Selection of a 'display MODE' will result in the same processing by Crunchy
as the selection of 'MODE' except that no interactive elements
(such as a Python interpreter)
will be inserted in the page, thereby preserving the normal browser
sandbox to protect your computer from malicious code.""")

        p = cp.SubElement(div, 'p')
        p.text = _("""
Crunchy will remove any pre-existing javascript code on the page as
well as a number of html elements that could be used to hide some
javascript code.
        """)

        p = cp.SubElement(div, 'p')
        p.text = _("""
'trusted' should only be used for sites that you are convinced will
not attempt to insert malicious code.  Sites that allow users to post
comments, or worse, that allow users to edit (such as wikis) should not
be set to 'trusted'. With 'trusted' selected, Crunchy will display the
site as closely as it can to the wayt the original looked using only
 your browser.
        """)

        p = cp.SubElement(div, 'p')
        p.text = _("""
'normal' will attempt to display the sites the same ways as 'trusted' does
except that it will remove any styling deemed suspicious (see the docs for
details) and will validate any image source before allowing the image to
be displayed.  If the site contains many images, this validation process
will slow down the display.  Images that can not be validated will not be
shown.  Each image is validated only once during a given Crunchy session.
        """)

        p = cp.SubElement(div, 'p')
        p.text = _("""
'strict' will remove all styling and image on the page.  It will result
in the fastest display, but one that will likely be the least visually
appealing.
        """)

    return

##def allow_site(request):
##    '''function used to have the user confirm the security level
##       for the site'''
##    global trusted_key, netloc
##
##    if request.data == "":
##        request.send_response(200)
##        request.end_headers()
##        request.wfile.write("asdf")
##        request.wfile.flush()
##        return
##
##    # create random site key or users to enter (not too long)
##    n = int(random.random()*1000000)
##    if n < 100000:
##        n = 999999 - n
##    trusted_key = str(n)
##
##    # print a trusted site key in the console
##    print "----------------------------------------------------"
##    print _("Host: ") + netloc
##    print _("Confirmation code: ") + trusted_key
##    print "----------------------------------------------------"
##
##    request.send_response(200)
##    request.end_headers()
##    request.wfile.flush()

### have the users enter a trusted site key to add the site to a list
##def enter_trusted_key(request):
##    global trusted_key, netloc
##    user_key = request.data
##
##    if user_key == trusted_key:
##        request.send_response(200)
##        request.end_headers()
##        request.wfile.write("Success")
##        request.wfile.flush()
##    else:
##        request.send_response(200)
##        request.end_headers()
##        request.wfile.write("Failed")
##        request.wfile.flush()

def set_security_list(request):
    print "called set_security_list"
    site_list_info = request.data.strip(',').split(',')
    print site_list_info
    site_list = []
    for site_info in site_list_info:
        if ":" not in site_info:
            continue
        site = site_info.split(':')
        mode = site[1].strip()
        site = site[0].strip()
        site_list.append(site)
        to_be_deleted = []
        print "site = ", site
        if site.strip() != '':
            if mode in ['trusted', 'normal', 'strict',
               'display normal', 'display strict', 'display trusted']:
                configuration.defaults._set_site_security(site, mode)
                if cp.DEBUG:
                    print '%s has been set to %s: '%(site, mode)
            else:
                to_be_deleted.append(site)
    for site in to_be_deleted:
        del configuration.defaults.site_security[site]
    # If we are approving a site for the first time, we don't need
    # the user to confirm again in this session, so assign
    # initial_security_set to True
    configuration.initial_security_set = True
    configuration.defaults._save_settings()

    request.send_response(200)
    request.end_headers()
    request.wfile.write("")
    request.wfile.flush()

def empty_security_list(request):
    sites = []
    for site in configuration.defaults.site_security:
        sites.append(site)
    for site in sites:
        del configuration.defaults.site_security[site]
    # If we are approving a site for the first time, we don't need
    # the user to confirm again in this session, so assign
    # initial_security_set to True
    configuration.initial_security_set = True
    configuration.defaults._save_settings()

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
    font: 12pt monospace;
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
