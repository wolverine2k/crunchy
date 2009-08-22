'''
security_advisor.py

Inserts security information about a given page
'''

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, translate, plugin, Element, SubElement, \
     additional_menu_items, python_version
_ = translate['_']

if python_version < 3:
    from urlparse import urlsplit
else:
    from urllib.parse import urlsplit

provides = set(["/allow_site", "/set_trusted", "/remove_all"])

DEBUG = False

def register():
    '''
    register a tag handler and two http handlers: /set_trusted and /remove_all
    '''
    plugin['register_begin_pagehandler'](insert_security_info)
    plugin['register_http_handler']("/set_trusted", set_security_list)
    plugin['register_http_handler']("/remove_all", empty_security_list)

def create_security_menu_item(page):
    '''creates the security report menu item'''

    if 'display' in page.security_info['level']:
        security_result_image = '/images/display.png'
    elif page.security_info['number removed'] == 0:
        security_result_image = '/images/ok.png'
    else:
        security_result_image = '/images/warning.png'

    security_item = Element("li")
    a = SubElement(security_item, "a", id="security_info_link", href="#",
                   onclick= "show_security_info();", title="security_link")
    a.text = "Security: "
    SubElement(a, "img", src=security_result_image)
    additional_menu_items['security_report'] = security_item
    return

def insert_security_info(page, *dummy):
    """Inserts security information on a page"""
    if not len(page.body):
        return

    create_security_menu_item(page)

    # Next, the hidden container for the full security information

    if not page.includes("security_included"):
        page.add_include("security_included")
        page.insert_js_file("/security.js")

        info_container = Element("div", id="security_info")

        # prompt user to approve sites as soon as the first page is loaded
        # if there are sites for which to confirm the security level.
        if ((page.url.startswith("/index") or page.url=="/")
                  # will work with /index_fr.html ...
              and config[page.username]['site_security']
                  # something to confirm
              and not config[page.username]['initial_security_set']):
                  # only do it once per session
            confirm_at_start(page, info_container)
            config[page.username]['initial_security_set'] = True
        else:
            page.add_css_code(security_css%('none','none'))
            format_report(page, info_container)

        page.body.append(info_container)
        info_container_x = Element("div", id="security_info_x",
                                        onclick="hide_security_info()")
        info_container_x.text = "X"
        page.body.append(info_container_x)

def confirm_at_start(page, info_container):
    '''
    Asks for confirmation from the user for any pre-existing settings
    regarding security level for known sites.

    This is meant to be called only at the start of a given Crunchy session
    (hence the name of the function).
    '''
    page.add_css_code(security_css%('block','block'))
    h2 = SubElement(info_container, 'h2')
    h2.text = _('Confirm the security levels')
    h2.attrib['class'] = "crunchy"
    directions = SubElement(info_container, "h4")
    directions.text = _("Before browsing any further ...\n\n")
    directions.text += _("Do you wish to retain the existing settings for these sites?\n\n")
    directions.text += _("You can change any of them before clicking on the approve button.\n\n")

    # in case list gets too long, we include buttons at top and bottom of list
    nb_sites = len(config[page.username]['site_security'])
    add_button(info_container, nb_sites)
    for site_num, site in enumerate(config[page.username]['site_security']):
        format_site_security_options(info_container, site, site_num, page)
    add_button(info_container, nb_sites)
    return

def format_site_security_options(parent, site, site_num, page):
    '''adds the various security options for a given site'''
    options = ['trusted', 'normal', 'strict', 'display trusted',
               'display normal', 'display strict']
    if 'localhost' not in site:
        options.append('remove')
    fieldset = SubElement(parent, "fieldset")
    site_label = SubElement(fieldset, "legend")
    site_label.text = site
    form = SubElement(fieldset, "form")
    form.attrib['id'] = "site_" + str(site_num+1)
    form.attrib['name'] = site
    for option in options:
        label = SubElement(form, 'label')
        if option == 'remove':
            label.text = _('remove from list')
        else:
            label.text = option
        label.attrib['for'] = site + option
        inp = SubElement(label, 'input', value=option, type='radio',
                                        name='rad', id=site+option)
        SubElement(form, 'br')
        if site in config[page.username]['site_security']:
            if option == config[page.username]['site_security'][site]:
                inp.attrib['checked'] = 'checked'
        elif 'localhost' in site:
            if option == config[page.username]['local_security']:
                inp.attrib['checked'] = 'checked'
    return

def add_button(info_container, nb_sites):
    '''adds button for site approval or removal'''
    approve_btn = SubElement(info_container, "button",
                                onclick = "app_approve(%d)" % nb_sites)
    approve_btn.text = _("Approve")
    SubElement(info_container, "span").text = " "
    deny_btn = SubElement(info_container, "button", onclick="app_remove_all()")
    deny_btn.text = _("Remove all")
    return

def format_table(parent, title, headings, content):
    '''formats a report in a standard table form'''
    h2 = SubElement(parent, 'h2')
    h2.text = title
    h2.attrib['class'] = "crunchy"

    table = SubElement(parent, 'table')
    table.attrib['class'] = 'summary'

    tr = SubElement(table, 'tr')
    for item in headings:
        th = SubElement(tr, 'th')
        th.text = item

    for item in content:
        tr = SubElement(table, 'tr')
        for cell in item:
            td = SubElement(tr, 'td')
            td.text = str(cell)
    return

intro_exp = _("""
Selection of a 'display MODE' will result in the same processing by Crunchy
 as the selection of 'MODE' except that no interactive elements
 (such as a Python interpreter)
 will be inserted in the page, thereby preserving the normal browser
 sandbox to protect your computer from malicious code.""")

intro2_exp = _("""
Crunchy will remove any pre-existing javascript code on the page as
 well as a number of html elements that could be used to hide some
 javascript code.""")

trusted_exp = _("""
'trusted' should only be used for sites that you are convinced will
 not attempt to insert malicious code.  Sites that allow users to post
 comments, or worse, that allow users to edit (such as wikis) should not
 be set to 'trusted'. With 'trusted' selected, Crunchy will display the
 site as closely as it can to the way the original looked using only
 your browser.""")

normal_exp = _("""
'normal' will attempt to display the sites the same ways as 'trusted' does
 except that it will remove any styling deemed suspicious (see the docs for
 details) and will validate any image source before allowing the image to
 be displayed.  If the site contains many images, this validation process
 will slow down the display.  Images that can not be validated will not be
 shown.  Each image is validated only once during a given Crunchy session.""")

strict_exp = _("""
'strict' will remove all styling and image on the page.  It will result
 in the fastest display, but one that will likely be the least visually
 appealing.""")

explanations = [intro_exp, intro2_exp, trusted_exp, normal_exp, strict_exp]

def format_report(page, div):
    '''puts the security information (extracted material) into a table
       for display'''

    security_level = SubElement(div, 'h2')
    security_level.attrib['class'] = 'crunchy'
    security_level.text = "Security level: " + page.security_info['level']

    security_summary = SubElement(div, 'h4')
    s_image = SubElement(security_summary, 'img')
    # make sure src link is not transformed:
    s_image.attrib['title'] = 'security_link'

    if 'display' in page.security_info['level']:
        s_image.attrib['src'] = '/images/display_big.png'
        s_image.tail = " : display mode selected; Python code execution forbidden."
    elif page.security_info['number removed'] == 0:
        s_image.attrib['src'] = '/images/ok_big.png'
        s_image.tail = " : clean page; nothing was removed by Crunchy."
    else:
        s_image.tail = " : Some html tags and/or attributes were removed by Crunchy."
        s_image.attrib['src'] = '/images/warning_big.png'

    if page.security_info['tags removed']:
        title = _('Removed: tag not allowed')
        headings = [_('Tag removed'), _('Number of times')]
        content = page.security_info['tags removed']
        format_table(div, title, headings, content)

    if page.security_info['attributes removed']:
        title = _('Removed: attribute, or attribute value not allowed')
        headings = [_('Tag'), _('Attribute'), _('Value (if relevant)')]
        content = page.security_info['attributes removed']
        format_table(div, title, headings, content)

    if page.security_info['styles removed']:
        title = _('Removed: style tag or attribute not allowed')
        headings = [_('Tag'), _('Attribute (if relevant)'), _('Value')]
        content = page.security_info['styles removed']
        format_table(div, title, headings, content)

    #netloc = urlsplit(page.url).netloc # localhost will return empty string
    # urlsplit().netloc == urlsplit()[1] is not Python 2.4 compatible
    netloc = urlsplit(page.url)[1]

    if netloc:
        site = netloc
    else:
        site = "localhost (127.0.0.1)"

    h2 = SubElement(div, 'h2')
    h2.text = _('You may select a site specific security level:')
    h2.attrib['class'] = "crunchy"
    if netloc in config[page.username]['site_security']:
        p = SubElement(div, 'p')
        p.text = _("If you want to preserve the existing selection, ")
        p.text += _("simply dismiss this window by clicking on the X above.")
    format_site_security_options(div, site, 0, page)

    approve_btn = SubElement(div, "button")
    approve_btn.attrib["onclick"] = "javascript:allow_site();"
    approve_btn.text = _("Select site security level")

    for item in explanations:
        p = SubElement(div, 'p')
        p.text = item
    return

def set_security_list(request):
    '''
    sets the security level for a number of sites on a list
    '''
    if python_version >= 3:
        request.data = request.data.decode('utf-8')
    site_list_info = request.data.strip(',').split(',')
    username = request.crunchy_username
    if DEBUG:
        print('inside set_security_list', site_list_info)
    to_be_deleted = []
    for site_info in site_list_info:
        if "::" not in site_info:
            if DEBUG:
                print(":: not in site_info")
            continue
        site = site_info.split('::')
        mode = site[1].strip()
        site = site[0].strip()
        if DEBUG:
            print("site = ", site)

        if 'localhost' not in site:
            if mode in ['trusted', 'normal', 'strict',
               'display normal', 'display strict', 'display trusted']:
                config[username]['_set_site_security'](site, mode)
                if DEBUG:
                    print(str(site) + ' has been set to ' + str(mode))
            else:
                to_be_deleted.append(site)
                if DEBUG:
                    print(str(site) + ' is going to be removed.')
        else:
            config[username]['_set_local_security'](mode)
            if DEBUG:
                print("setting local security to ", mode)
            break  # should be only site

    for site in to_be_deleted:
        del config[username]['site_security'][site]
    if DEBUG:
        print(config[username]['site_security'])
    # If we are approving a site for the first time, we don't need
    # the user to confirm again in this session, so assign
    # initial_security_set to True
    config[username]['initial_security_set'] = True
    config[username]['_save_settings']()

    request.send_response(200)
    request.end_headers()
    request.wfile.write("".encode('utf-8'))
    request.wfile.flush()

def empty_security_list(request):
    '''
    removes all the sites from the list of sites with security level assigned
    '''
    username = request.crunchy_username
    sites = []
    for site in config[username]['site_security']:
        sites.append(site)
    for site in sites:
        del config[username]['site_security'][site]
    # We don't need the user to confirm again in this session, so assign
    # initial_security_set to True
    config[username]['initial_security_set'] = True
    config[username]['_save_settings']()

    request.send_response(200)
    request.end_headers()
    request.wfile.write("".encode('utf-8'))
    request.wfile.flush()

# Note: the rest of the css appears in crunchy.css
security_css = """
#security_info {
    display: %s;  /* will appear only when needed */
}
#security_info_x {
    display: %s;  /* will appear only when needed */
}
"""
