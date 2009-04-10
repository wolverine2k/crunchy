"""
config_gui.py : a plugin to enable users to configure crunchy nicely.

"""
from src.interface import plugin, config, SubElement, Element, translate,\
   additional_menu_items
_ = translate['_']
import src.configuration as configuration

def register():
    '''registers two http handlers: /config and /set_config and a begin page
    handler to insert the configuration page'''
    plugin['register_http_handler'](
                    "/set_config%s" % plugin['session_random_id'], set_config)
    plugin['register_tag_handler']("div", "title", "preferences", insert_preferences)

    plugin['register_begin_pagehandler'](add_configuration_to_menu)

def add_configuration_to_menu(page):
    '''adds a menu item allowing the user to choose the preferences'''
    menu_item = Element("li")
    link = SubElement(menu_item, 'a', href="/docs/basic_tutorial/preferences.html")
    link.text = _("Preferences")
    additional_menu_items['preferences'] = menu_item

def insert_preferences(page, elem, uid):
    '''insert the requested preference choosers on a page'''
    if not page.includes("set_config"):
        page.add_include("set_config")
        page.add_js_code(set_config_jscode)
    # The original div in the raw html page may contain some text
    # as a visual reminder that we need to remove here.
    elem.text = ''
    elem.attrib['class'] = 'config_gui'
    parent = SubElement(elem, 'table')
    username = page.username
    to_show = elem.attrib['title'].split(' ')
    if len(to_show) == 1: # choices = "preferences"; all values are shown
        to_show = ['boolean', 'multiple_choice', 'user_defined']
    show(parent, username, uid, to_show)
    return

def set_config(request):
    """Http handler to set an option"""
    info = request.data.split("__SEPARATOR__")
    key = info[0]
    value = info[-1]
    if value == 'on':
        _id = info[1]
        if '__VALUE__' in _id:
            value = _id.split("__VALUE__")[1]
    option = ConfigOption.all_options[key]
    option.set(value)

def show(parent, username, uid, to_show=None):
    '''Shows all the requested configuration options in alphabetical order.'''
    if to_show is None:
        return
    keys = []

    for key in config[username]:
        if not (key in get_prefs(username)._not_saved or key.startswith('_')):
            _type = select_option_type(key, username, uid)
            if (_type in to_show) or (key in to_show):
                keys.append(key)

    #for key in configuration.options:
    #    _type = select_option_type(key, username, uid)
    #    if (_type in to_show) or (key in to_show):
    #        keys.append(key)
    keys.sort()
    for key in keys:
        ConfigOption.all_options[key].render(parent)
    return

def select_option_type(key, username, uid, allowed_options=configuration.options,
                       ANY=configuration.ANY):
    '''select the option type to choose based on the key requested'''
    excluded = ['site_security', 'log_filename']
    if key in config[username] and key not in excluded:
        if set(allowed_options[key]) == set((True, False)):
            BoolOption(key, config[username][key], username, uid)
            _type = 'boolean'
        elif ANY in allowed_options[key]:
            StringOption(key, config[username][key], username, uid)
            _type = 'user_defined'
        elif key in allowed_options:
            MultiOption(key, config[username][key], allowed_options[key],
                        username, uid)
            _type = 'multiple_choice'
        else:
            print "Unexpected error in select_option_type; option = ", key
            print "not found in configuration.options but found in config[]."
    else:
        print key, "is not a valid configuration option"
        return False
    return _type

def get_prefs(username):
    """Return the preference object"""
    return config[username]['symbols'][config[username]['_prefix']]

class ConfigOption(object):
    """Generic option class"""
    all_options = {}

    def __init__(self, key, initial, username=None, uid=None):
        self.key = key
        self.uid = uid
        self.username = username
        self.set(initial)
        ConfigOption.all_options[key] = self

    def get(self):
        """Return the current value of the option"""
        return self.value

    def set(self, value):
        """sets and saves the value of the option"""
        self.value = value
        get_prefs(self.username)._save_settings(self.key, value)

class MultiOption(ConfigOption):
    """An option that has multiple predefined choices
    """
    # the threshold between radio buttons and a dropdown box
    threshold = 6

    def __init__(self, key, initial, values, username=None, uid=None):
        self.values = values
        super(MultiOption, self).__init__(key, initial, username=username, uid=uid)

    def get_values(self):
        """get the possible values"""
        return self.values

    def set(self, value):
        """Define the value of the option
        Convert str(None) in the python None object only if needed.
        """
        if None in self.get_values() and value == str(None):
            value = None
        super(MultiOption, self).set(value)

    def render(self, elem):
        """render the widget to a particular file object"""
        values = self.get_values()
        row = SubElement(elem, 'tr')
        option = SubElement(row, 'td')
        # we use a unique id, rather than simply the key, in case two
        # identical preference widgets are on the same page...
        if len(values) <= MultiOption.threshold:
            option.text = "%s: " % self.key
            SubElement(option, 'br')
            form = SubElement(option, 'form')
            for value in values:
                _id = str(self.uid) + "__VALUE__" + str(value)
                input = SubElement(form, 'input',
                    type = 'radio',
                    name = self.key,
                    id = _id,
                    onchange = "set_config('%(id)s', '%(key)s');" \
                        % {'id': _id, 'key': self.key},
                )
                if value == self.get():
                    input.attrib['checked'] = 'checked'
                label = SubElement(form, 'label')
                label.attrib['for'] = "%s_%s" % (self.key, str(value))
                label.text = str(value)
                SubElement(form, 'br')
        else:
            _id = str(self.uid) + "__KEY__" + str(self.key)
            label = SubElement(option, 'label')
            label.attrib['for'] = self.key
            label.text = "%s: " % self.key
            select = SubElement(option, 'select',
                name = self.key,
                id = _id,
                onchange = "set_config('%s', '%s');" % (_id, self.key)
            )
            for value in values:
                select_elem = SubElement(select, 'option', value = str(value))
                if value == self.get():
                    select_elem.attrib['selected'] = 'selected'
                select_elem.text = str(value) # str( ) is needed for None
        desc = SubElement(row, 'td')
        desc.text = str(getattr(get_prefs(self.username).__class__, self.key).__doc__)

class BoolOption(ConfigOption):
    """An option that has two choices [True, False]
    """
    def render(self, elem):
        """render the widget to a particular file object"""
        row = SubElement(elem, 'tr')
        option = SubElement(row, 'td')
        # we use a unique id, rather than simply the key, in case two
        # identical preference widgets are on the same page...
        _id = str(self.uid) + "__KEY__" + str(self.key)
        input = SubElement(option, 'input',
            type = 'checkbox',
            name = self.key,
            id = _id,
            onchange = "set_config('%s', '%s');" % (_id, self.key)
        )
        if self.get():
            input.attrib['checked'] = 'checked'
        label = SubElement(option, 'label')
        label.attrib['for'] = self.key
        label.text = self.key
        desc = SubElement(row, 'td')
        desc.text = str(getattr(get_prefs(self.username).__class__, self.key).__doc__)

    def set(self, value):
        """Define the value of the option
        This function replace the javascript "true" and "false" values, which
        may be returned by some http_hanlder, by python objects True and False.
        """
        # Note: value could already be True...
        if value == "true" or value == True:
            value = True
        else:
            value = False
        super(BoolOption, self).set(value)

class StringOption(ConfigOption):
    """An option that can have any value
    """
    def render(self, elem):
        """render the widget to a particular file object"""
        row = SubElement(elem, 'tr')
        option = SubElement(row, 'td')
        label = SubElement(option, 'label')
        label.attrib['for'] = self.key
        label.text = "%s: " % self.key
        # we use a unique id, rather than simply the key, in case two
        # identical preference widgets are on the same page...
        _id = str(self.uid) + "__KEY__" + str(self.key)
        input = SubElement(option, 'input',
            type = 'text',
            id = _id,
            name = self.key,
            value = self.get(),
            onchange = "set_config('%s', '%s');" % (_id, self.key)
        )
        input.attrib['class'] = 'config_gui'
        desc = SubElement(row, 'td')
        desc.text = str(getattr(get_prefs(self.username).__class__, self.key).__doc__)

set_config_jscode = """
function set_config(id, key){
    var value;
    field=document.getElementById(id);
    // find the value depending of the type of input
    if (field.type == 'checkbox') {
        value = field.checked;
    }
    else if (field.type != 'radio'){
        value = field.value;
    }
    else{
        value = id + "__SEPARATOR__" + field.value
    }

    // if needed, send the new value
    if (value != undefined) {
        var j = new XMLHttpRequest();
        j.open("POST", "/set_config%s", false);
        j.send(key+"__SEPARATOR__"+value);
    }
};
""" % plugin['session_random_id']
