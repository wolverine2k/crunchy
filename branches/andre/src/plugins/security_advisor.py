'''
security_advisor.py

Inserts security information at the top of a page
'''

import src.CrunchyPlugin as cp
def register():
    cp.register_tag_handler("no_tag", "security", None, insert_security_info)

def insert_security_info(page, *dummy):
    """Inserts security information at the top of a page"""
    if not page.body:
        return

    #===First, the static display at the top

    if 'trusted' in page.security_info['level']:
        src = '/trusted.png'
    elif 'normal' in page.security_info['level']:
        src = '/normal.png'
    elif 'severe' in page.security_info['level']:
        src = '/severe.png'
    elif 'paranoid' in page.security_info['level']:
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
        page.add_css_code(security_css)

        info_container = cp.Element("div")
        info_container.attrib["id"] = "security_info"
        format_report(page, info_container)
        #info_container.text = "Here's the information\n more information "
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

    return

security_css = """
#security_info {
    position: fixed;
    top: 60px;
    right: 400px;
    width: 50%;
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
    display: none;  /* will appear only when needed */
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
    display: none;  /* will appear only when needed */
    z-index:12;
}
"""
