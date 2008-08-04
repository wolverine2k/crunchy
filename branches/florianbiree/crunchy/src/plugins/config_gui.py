"""
config_gui.py : a plugin to enable users to configure crunchy nicely.

"""

import os.path
import StringIO
from src.interface import translate, plugin, config
from src.interface import parse, SubElement, tostring
_ = translate['_']
# TODO: get those object from src.interface instead
from src.configuration import options, ANY

provides = set(["/comet", "/input"])

def register():  # tested
    '''registers two http handlers: /config and /set_config and a begin page
    handler to insert the configuration page'''
    plugin['register_http_handler'](
                    "/set_config%s" % plugin['session_random_id'], set_config)
    plugin['register_http_handler']("/config", config_page)

# the following are required for Crunchy to work; they will need to be defined.
def set_config(request):
    """Http handler to set an option"""
    key = request.args['key']
    value = request.args['value']
    option = ConfigOption.all_options[key]
    option.set(value)
    
def config_page(request):
    """Http handler to make a dynamic configuration page"""
    # Dynamic generation of the option list
    for key in options:
        if key in config:
            if set(options[key]) == set((True, False)):
                # boolean option
                BoolOption(key, config[key])
            elif ANY in options[key]:
                # any string allowed
                StringOption(key, config[key])
            else:
                # multiple predefined choices
                MultiOption(key, config[key], options[key])
    
    # Getting the main template from server_root/index.html
    html = parse(index_path)
    # Find the head
    head = html.find('head')
    script = SubElement(head, 'script', type='text/javascript')
    script.text = set_config_jscode
    SubElement(head, 'style').text = option_style
    # Set the title
    head.find('title').text = _("Configuration")
    titlebar = [element for element in html.getiterator() \
                     if element.attrib.get('id') == 'titlebar'][0]
    titlebar.find('h1').text = _("Configuration")
    # Find the content div
    content_block = [element for element in html.getiterator() \
                     if element.attrib.get('id') == 'content'][0]
    # Remove its content
    for content in content_block:
        content_block.remove(content)
    content_block.text = ""
    
    # Rendering the page
    option_list = SubElement(content_block, 'dl')
    # Sort options in the lphabetical order
    keys = ConfigOption.all_options.keys()
    keys.sort()
    for key in keys:
        ConfigOption.all_options[key].render(option_list)
    
    # Send the page
    request.wfile.write(tostring(html.getroot()))

def get_prefs():
    """Return the preference object"""
    return config['symbols'][config['_prefix']]

class ConfigOption(object):     # tested
    """Generic option class"""
    all_options = {}

    def __init__(self, key, initial):       # tested
        self.key = key
        self.set(initial)
        ConfigOption.all_options[key] = self

    def get(self):      # tested
        """Return the current value of the option"""
        return self.__value

    def set(self, value):
        """Define the value of the option
        """
        self.__value = value
        #Need to use that instead of config[self.key] = value to save values...
        # TODO: find a better way to save settings
        setattr(get_prefs(), self.key, value)

class MultiOption(ConfigOption):        # tested
    """An option that has multiple predefined choices
    """
    # the threshold between radio buttons and a dropdown box
    threshold = 4

    def __init__(self, key, initial, values):       # tested
        self.values = values
        super(MultiOption, self).__init__(key, initial)
    
    def get_values(self):       # tested
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
        option = SubElement(elem, 'dt')
        if len(values) <= MultiOption.threshold:
            option.text = "%s: " % self.key
            SubElement(option, 'br')
            for value in values:
                input = SubElement(option, 'input',
                    type = 'radio',
                    name = self.key,
                    id = "%s_%s" % (self.key, str(value)),
                    value = str(value), # str( ) is needed for None
                    onchange = "set_config('%(key)s_%(value)s', '%(key)s');" \
                        % {'key': self.key, 'value': str(value)},
                )
                if value == self.get():
                    input.attrib['checked'] = 'checked'
                label = SubElement(option, 'label')
                label.attrib['for'] = "%s_%s" % (self.key, str(value))
                label.text = str(value)
                SubElement(option, 'br')
        else:
            label = SubElement(option, 'label')
            label.attrib['for'] = self.key
            label.text = "%s: " % self.key
            select = SubElement(option, 'select',
                name = self.key,
                id = self.key,
                onchange = "set_config('%(key)s', '%(key)s');" % \
                    {'key': self.key},
            )
            for value in values:
                select_elem = SubElement(select, 'option', value = str(value))
                if value == self.get():
                    select_elem.attrib['selected'] = 'selected'
                select_elem.text = str(value) # str( ) is needed for None
        desc = SubElement(elem, 'dd')
        desc.text = str(getattr(get_prefs().__class__, self.key).__doc__)

class BoolOption(ConfigOption):
    """An option that has two choices [True, False]
    """
    
    def render(self, elem):
        """render the widget to a particular file object"""
        option = SubElement(elem, 'dt')
        input = SubElement(option, 'input',
            type = 'checkbox',
            name = self.key,
            id = self.key,
            onchange = "set_config('%(key)s', '%(key)s');" % {'key': self.key},
        )
        if self.get:
            input.attrib['checked'] = 'checked'
        label = SubElement(option, 'label')
        label.attrib['for'] = self.key
        label.text = self.key
        desc = SubElement(elem, 'dd')
        desc.text = str(getattr(get_prefs().__class__, self.key).__doc__)
    
    def set(self, value):
        """Define the value of the option
        This function replace the javascript "true" and "false value by python
        objects True and False.
        """
        if value == "true":
            value = True
        elif value == "false":
            value = False
        super(BoolOption, self).set(value)

class StringOption(ConfigOption):
    """An option that can have any value
    """
    
    def render(self, elem):
        """render the widget to a particular file object"""
        option = SubElement(elem, 'dt')
        label = SubElement(option, 'label')
        label.attrib['for'] = self.key
        label.text = "%s: " % self.key
        input = SubElement(elem, 'input',
            type = 'text',
            id = self.key,
            name = self.key,
            value = self.get(),
            onchange = "set_config('%(key)s', '%(key)s');" % {'key': self.key},
        )
        desc = SubElement(elem, 'dd')
        desc.text = str(getattr(get_prefs().__class__, self.key).__doc__)

index_path = os.path.join(plugin['get_root_dir'](), "server_root/template.html")

set_config_jscode = """
function set_config(id, key){
    var value;
    field=document.getElementById(id)
    // find the value depending of the type of input
    if (field.type == 'checkbox') {
        value = field.checked;
    }
    else if ((field.type != 'radio') || (field.checked)) {
        // exclude unchecked radio
        value = field.value;
    }
    
    // if needed, send the new value
    if (value != undefined) {
        var j = new XMLHttpRequest();
        j.open("POST", "/set_config%s?key="+key+"&value="+value, false);
        j.send(key+"_::EOF::_"+value);
    }
};
""" % plugin['session_random_id']

option_style = """
dd{
    position:relative;
    top: -1em;
    text-align:right;
    border-bottom: 1px dotted black;
}
"""
