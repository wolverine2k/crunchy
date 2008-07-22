"""  Menu plugin.

Other than through a language preference, Crunchy menus can be modified
by plugin writers who can add other items.
"""

from src.interface import plugin, Element, SubElement, config, \
     translate, additional_menu_items
_ = translate['_']


def register(): # tested
    """
       registers the tag handlers for inserting menu as well as
       allowed positions for the menu.
    """
    plugin['register_end_pagehandler'](insert_menu)
    plugin['add_vlam_option']('menu_position', 'top_left', 'top_right',
                              'bottom_right', 'bottom_left')

def create_empty_menu(): # tested
    '''creates the basic menu structure including only the title'''
    menu = Element('div')
    menu.attrib['class'] = "menu"
    _ul = SubElement(menu, "ul")
    _li = SubElement(_ul, "li")
    _li.text = _("Crunchy Menu")
    menu_items = SubElement(_li, "ul")
    return menu, menu_items

def create_home():  # tested
    '''creates the home element for the menu'''
    home = Element("li")
    a = SubElement(home, "a", href="/index.html")
    a.text = _("Crunchy Home")
    return home

def create_quit(): # tested
    '''creates the quit element for the menu'''
    Quit = Element("li")
    a = SubElement(Quit, "a", href="/exit")
    a.text = _("Quit Crunchy")
    return Quit

def insert_menu(page): # tested
    """inserts the default Crunchy menu, if no other menu is present."""
    menu, menu_items = create_empty_menu()
    menu_items.append(create_home())
    for item in additional_menu_items:
        if item.startswith('0'):
            menu_items.insert(0, additional_menu_items[item])
        else:
            menu_items.append(additional_menu_items[item])
    menu_items.append(create_quit())
    if page.body:
        page.body.insert(0, menu)

    height = 20
    bottom = "bottom:%spx;" % height
    top = "top:%spx;" % height
    width = 150
    padding = 5
    items_width = width - 2*padding
    if config['menu_position'] == 'top_right':
        menu_position = menu_position_css % ("top:0; right:0;", top,
                                            height, height)
    elif config['menu_position'] == 'top_left':
        menu_position = menu_position_css % ("top:0; left:0;", top,
                                            height, height)
    elif config['menu_position'] == 'bottom_right':
        menu_position = menu_position_css % ("bottom:0; right:0;", bottom,
                                            height, height)
    elif config['menu_position'] == 'bottom_left':
        menu_position = menu_position_css % ("bottom:0; left:0;", bottom,
                                            height, height)
    else:  # use top_right as default
        menu_position = menu_position_css % ("top:0; right:0;", top,
                                            height, height)

    _css = menu_css % (menu_position, items_width, items_width,
                       padding, padding, width)
    try:
        page.add_css_code(_css)
    except Exception:#, info:
        print("Cannot append css code in the head") # info
    return

menu_position_css = """
.menu {%s}
.menu ul li:hover ul, .menu ul li a:hover ul {%s}
.menu ul li , .menu ul li a, .menu ul li a:visited {
height:%spx; line-height:%spx;}
"""

# example 1: %(location, vertical_location, height, height)
#           location = bottom:0; right:0;
#           vertical_location = bottom:25px;
#           height=25

# example 2: location = top:0; left:0;
#           vertical_location = top:0;
#           height=25

# insert menu_position_css into menu_css below
menu_css = """%s
.menu {
    position:fixed;
    font-size:11pt;
    width:%spx;
}
.menu ul {
    padding:0;
    margin:0;
    list-style-type: none;
}
.menu ul li ul {
    visibility:hidden;
    position:absolute;
}
.menu ul li a, .menu ul li a:visited {
    display:block;
    text-decoration:none;
    width:%spx;
    text-align:left;
    color:#fff;
    padding:0 %spx 0 %spx;
    background:#369;
}

.menu ul li{
    display:block;
    width:%spx;
    text-align:center;
    color:#fff;
    background:#369;
    border-bottom: 1px solid #fff;
}
.menu ul li:hover ul, .menu ul li a:hover ul {
    visibility:visible;
}
.menu ul li:hover ul li a {
    background:#4682b5;
color:#fff;
}
.menu ul li:hover ul li a:hover {
    background:#e9e9c7;
    color:#000;
}
"""
