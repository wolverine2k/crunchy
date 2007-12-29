'''
security_advisor.py

Inserts security information at the top of a page
'''
from urlparse import urlsplit

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, translate, plugin, Element, SubElement
_ = translate['_']

provides = set(["/allow_site", "/enter_key", "/set_trusted", "/remove_all"])

DEBUG = False

def register():
    plugin['register_tag_handler']("no_tag", "security", None, insert_security_info)
    plugin['register_http_handler']("/set_trusted", set_security_list)
    plugin['register_http_handler']("/remove_all", empty_security_list)

def insert_security_info(page, *dummy):
    """Inserts security information on a page"""
    if not page.body:
        return

    #===First, the static display at the top

    if 'trusted' in page.security_info['level']:
        src = '/trusted.png'
    elif 'normal' in page.security_info['level']:
        src = '/severe.png'
    elif 'strict' in page.security_info['level']:
        src = '/paranoid.png'

    span = Element("div")
    span.attrib['class'] = "security_report" # in file menu_basic.css
    span.attrib['id'] = "security_report"
    level_img = SubElement(span, "img")
    level_img.attrib["src"] = src
    level_img.attrib["alt"] = "security level image"
    level_img.attrib["style"] = "border:0;height:12pt"
    level_img.tail = _(" Crunchy security level: ") +\
                        page.security_info['level']

    SubElement(span, "br")

    img = SubElement(span, "img")
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
#    if not page.url.startswith("/"):
    if not page.security_info['number removed'] == 0:
        view = SubElement(span, "a")
        view.attrib["onclick"] = "show_security_info();"
        view.attrib["href"] = "#"
        view.attrib['style'] = "text-decoration: underline;"
        view.text = _(" View report ")
    br = SubElement(span, "br")
    hide = SubElement(span, "a")
    hide.attrib["onclick"] = "hide_security_report();"
    hide.attrib["href"] = "#"
    hide.attrib['style'] = "text-decoration: underline overline;"
    
    hide.text = _(" | Hide summary |")

    # make the advisory draggable; insert the required code
    if not page.includes("drag_included"):
        page.add_include("drag_included")
        page.insert_js_file("/drag.js")
    span.attrib['onmousedown'] = "dragStart(event, 'security_report')"

    page.body.insert(0, span)

    # Next, the hidden container for the full security information

    if not page.includes("security_included"):
        page.add_include("security_included")
        page.insert_js_file("/security.js")

        info_container = Element("div")
        info_container.attrib["id"] = "security_info"
        format_report(page, info_container)

        # prompt user to approve sites as soon as the first page is loaded
        # if there are sites for which to confirm the security level.
        if (page.url.startswith("/index")
                  # will work with /index_fr.html ...
              and config['site_security']
                  # something to confirm
              and not config['initial_security_set']):
                  # only do it once per session
            config['initial_security_set'] = True
            page.add_css_code(security_css%('block','block'))
            h2 = SubElement(info_container, 'h2')
            h2.text = _('Confirm the security levels')
            h2.attrib['class'] = "crunchy"
            directions = SubElement(info_container, "h4")
            directions.text = _("Before browsing any further ...\n\n")
            directions.text += _("Do you wish to retain the existing settings for these sites?\n\n")
            directions.text += _("You can change any of them before clicking on the approve button.\n\n")

            # in case list gets too long, we include buttons at top and bottom
            approve_btn = SubElement(info_container, "button")
            site_num = len(config['site_security'])
            approve_btn.attrib["onclick"] = "app_approve('%d')"%site_num
            approve_btn.text = _("Approve")
            SubElement(info_container, "span").text = " "
            deny_btn = SubElement(info_container, "button")
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
            for site in config['site_security']:
                site_num += 1
                fieldset = SubElement(info_container, "fieldset")
                site_label = SubElement(fieldset, "legend")
                site_label.text = site
                form = SubElement(fieldset, "form")
                form.attrib['id'] = "site_" + str(site_num)
                form.attrib['name'] = site
                for option in options:
                    label = SubElement(form, 'label')
                    label.text = option[1]
                    label.attrib['for'] = site + option[0]
                    inp = SubElement(label, 'input')
                    inp.attrib['value'] = option[0]
                    inp.attrib['type'] = 'radio'
                    inp.attrib['name'] = "rad"
                    inp.attrib['id'] = site + option[0]
                    br = SubElement(form, 'br')
                    if option[1] == config['site_security'][site]:
                        inp.attrib['checked'] = 'checked'
            # in case list gets too long, we include buttons at top and bottom
            approve_btn = SubElement(info_container, "button")
            approve_btn.attrib["onclick"] = "app_approve('%d')"%site_num
            approve_btn.text = _("Approve")
            SubElement(info_container, "span").text = " "
            deny_btn = SubElement(info_container, "button")
            deny_btn.attrib["onclick"] = "app_remove_all()"
            deny_btn.text = _("Remove all")
        else:
            page.add_css_code(security_css%('none','none'))

        page.body.append(info_container)

        info_container_x = Element("div")
        info_container_x.attrib["id"] = "security_info_x"
        info_container_x.attrib["onclick"] = "hide_security_info()"
        info_container_x.text = "X"
        page.body.append(info_container_x)

def format_report(page, div):
    '''puts the security information (extracted material) into a table
       for display'''
    global netloc
    if page.security_info['tags removed']:
        h2 = SubElement(div, 'h2')
        h2.text = _('Removed: tag not allowed')
        h2.attrib['class'] = "crunchy"

        table = SubElement(div, 'table')
        table.attrib['class'] = 'summary'
        tr = SubElement(table, 'tr')
        th = SubElement(tr, 'th')
        th.text = _('Tag removed')
        th = SubElement(tr, 'th')
        th.text = _('Number of times')

        for item in page.security_info['tags removed']:
            tr = SubElement(table, 'tr')
            td = SubElement(tr, 'td')
            td.text = item[0]
            td = SubElement(tr, 'td')
            td.text = str(item[1])

    if page.security_info['attributes removed']:
        h2 = SubElement(div, 'h2')
        h2.text = _('Removed: attribute, or attribute value not allowed')
        h2.attrib['class'] = "crunchy"

        table = SubElement(div, 'table')
        table.attrib['class'] = 'summary'

        tr = SubElement(table, 'tr')
        th = SubElement(tr, 'th')
        th.text = _('Tag')
        th = SubElement(tr, 'th')
        th.text = _('Attribute')
        th = SubElement(tr, 'th')
        th.text = _('Value (if relevant)')

        for item in page.security_info['attributes removed']:
            tr = SubElement(table, 'tr')
            td = SubElement(tr, 'td')
            td.text = item[0]
            td = SubElement(tr, 'td')
            td.text = item[1]
            td = SubElement(tr, 'td')
            td.text = item[2]

    if page.security_info['styles removed']:
        h2 = SubElement(div, 'h2')
        h2.text = _('Removed: style tag or attribute not allowed')
        h2.attrib['class'] = "crunchy"

        table = SubElement(div, 'table')
        table.attrib['class'] = 'summary'

        tr = SubElement(table, 'tr')
        th = SubElement(tr, 'th')
        th.text = _('Tag')
        th = SubElement(tr, 'th')
        th.text = _('Attribute (if relevant)')
        th = SubElement(tr, 'th')
        th.text = _('Value')

        for item in page.security_info['styles removed']:
            tr = SubElement(table, 'tr')
            td = SubElement(tr, 'td')
            td.text = item[0]
            td = SubElement(tr, 'td')
            td.text = item[1]
            td = SubElement(tr, 'td')
            td.text = item[2]

    #netloc = urlsplit(page.url).netloc # localhost will return empty string
    # urlsplit().netloc == urlsplit()[1] is not Python 2.4 compatible
    netloc = urlsplit(page.url)[1]     

    if page.security_info['number removed'] != 0 and netloc:
        h2 = SubElement(div, 'h2')
        h2.text = _('You may select a site specific security level:')
        h2.attrib['class'] = "crunchy"
        if netloc in config['site_security']:
            p = SubElement(div, 'p')
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

        fieldset = SubElement(div, "fieldset")
        site_label = SubElement(fieldset, "legend")
        site_label.text = netloc
        form = SubElement(fieldset, "form")
        form.attrib['id'] = "single_site_" + str(site_num)
        form.attrib['name'] = netloc
        for option in options:
            label = SubElement(form, 'label')
            label.text = option[1]
            label.attrib['for'] = netloc + option[0]
            inp = SubElement(label, 'input')
            inp.attrib['value'] = option[0]
            inp.attrib['type'] = 'radio'
            inp.attrib['name'] = "rad"
            inp.attrib['id'] = netloc + option[0]
            SubElement(form, 'br')
            if netloc in config['site_security']:
                if option[1] == config['site_security'][netloc]:
                    inp.attrib['checked'] = 'checked'
        approve_btn = SubElement(div, "button")
        approve_btn.attrib["onclick"] = "javascript:allow_site();"
        approve_btn.text = _("Select site security level")

        p = SubElement(div, 'p')
        p.text = _("""
Selection of a 'display MODE' will result in the same processing by Crunchy
as the selection of 'MODE' except that no interactive elements
(such as a Python interpreter)
will be inserted in the page, thereby preserving the normal browser
sandbox to protect your computer from malicious code.""")

        p = SubElement(div, 'p')
        p.text = _("""
Crunchy will remove any pre-existing javascript code on the page as
well as a number of html elements that could be used to hide some
javascript code.
        """)

        p = SubElement(div, 'p')
        p.text = _("""
'trusted' should only be used for sites that you are convinced will
not attempt to insert malicious code.  Sites that allow users to post
comments, or worse, that allow users to edit (such as wikis) should not
be set to 'trusted'. With 'trusted' selected, Crunchy will display the
site as closely as it can to the wayt the original looked using only
 your browser.
        """)

        p = SubElement(div, 'p')
        p.text = _("""
'normal' will attempt to display the sites the same ways as 'trusted' does
except that it will remove any styling deemed suspicious (see the docs for
details) and will validate any image source before allowing the image to
be displayed.  If the site contains many images, this validation process
will slow down the display.  Images that can not be validated will not be
shown.  Each image is validated only once during a given Crunchy session.
        """)

        p = SubElement(div, 'p')
        p.text = _("""
'strict' will remove all styling and image on the page.  It will result
in the fastest display, but one that will likely be the least visually
appealing.
        """)

    return

def set_security_list(request):
    site_list_info = request.data.strip(',').split(',')
    if DEBUG:
        print(site_list_info)
    site_list = []
    for site_info in site_list_info:
        if ":" not in site_info:
            continue
        site = site_info.split(':')
        mode = site[1].strip()
        site = site[0].strip()
        site_list.append(site)
        to_be_deleted = []
        if site.strip() != '':
            if mode in ['trusted', 'normal', 'strict',
               'display normal', 'display strict', 'display trusted']:
                config['_set_site_security'](site, mode)
                if DEBUG:
                    print(str(site) + ' has been set to ' + str(mode))
            else:
                to_be_deleted.append(site)
    for site in to_be_deleted:
        del config['site_security'][site]
    # If we are approving a site for the first time, we don't need
    # the user to confirm again in this session, so assign
    # initial_security_set to True
    config['initial_security_set'] = True
    config['_save_settings']()

    request.send_response(200)
    request.end_headers()
    request.wfile.write("")
    request.wfile.flush()

def empty_security_list(request):
    sites = []
    for site in config['site_security']:
        sites.append(site)
    for site in sites:
        del config['site_security'][site]
    # If we are approving a site for the first time, we don't need
    # the user to confirm again in this session, so assign
    # initial_security_set to True
    config['initial_security_set'] = True
    config['_save_settings']()

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
