"""
config_gui.py : a plugin to enable users to configure crunchy nicely.

"""

from src.interface import translate, plugin, config
from src.configuration import options, ANY
_ = translate['_']

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
    option = ConfigOption.all_options[request.args['option']]
    option.set(request.args['value'])
    
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
    # Rendering the page
    request.wfile.write(config_head_html)
    for key in ConfigOption.all_options:
        ConfigOption.all_options[key].render(request.wfile)
    request.wfile.write(config_tail_html)

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

    def set(self, value):   # tested
        """Define the value of the option"""
        self.__value = value

class MultiOption(ConfigOption):        # tested
    """An option that has multiple predefined choices
    """
    # the threshold between radio buttons and a dropdown box
    threshold = 4

    def __init__(self, key, initial, values):       # tested
        super(MultiOption, self).__init__(key, initial)
        self.values = values

    def get_values(self):       # tested
        """get the possible values"""
        return self.values

    def render(self, handle):
        """render the widget to a particular file object"""
        values = self.get_values()
        handle.write('<p>\n')
        if len(values) <= MultiOption.threshold:
            handle.write('%(name)s:<br />\n' % {'name': self.key})
            for value in values:
                handle.write('''
                <input type="radio" name="%(key)s" id="%(key)s-%(value)s"
                value="%(value)s" %(checked)s />
                <label for="%(key)s-%(value)s">%(value)s</label>
                <br />
                ''' % {
                    'key': self.key,
                    'value': str(value), # str( ) is needed for None
                    'checked': 'checked="checked"' if value == self.get() \
                                                   else '',
                })
                # TODO insert some javasrcipt
        else:
            handle.write('''
            <label for="%(key)s">%(name)s</label>:
            <select name="%(key)s" id="%(key)s">
            ''' % {
                'key': self.key,
                'name': self.key,
            })
            for value in values:
                handle.write('''
                <option value="%(value)s" %(selected)s>%(value)s</option>
                ''' % {
                    'value': str(value), # str( ) is needed for None
                    'selected': 'selected="selected"' if value == self.get() \
                                                      else '',
                }) 
                # TODO insert some javasrcipt
            handle.write("</select>")
        handle.write("</p>")

class BoolOption(ConfigOption):
    """An option that has two choices [True, False]
    """
    
    def render(self, handle):
        """render the widget to a particular file object"""
        handle.write('''
        <p>
            <input type="checkbox" name="%(key)s" id="%(key)s" %(checked)s />
            <label for="%(key)s">%(name)s</label>
        </p>
        ''' % {
            'key': self.key,
            'name': self.key,
            'checked': 'checked="checked"' if self.get() else '',
        })
        # TODO insert some javasrcipt

class StringOption(ConfigOption):
    """An option that can have any value
    """
    
    def render(self, handle):
        """render the widget to a particular file object"""
        handle.write('''
        <p>
            <label for="%(key)s">%(name)s</label>:
            <input type="text" id="%(key)s" name="%(key)s" value="%(value)s" />
        </p>
        ''' % {
            'key': self.key,
            'name': self.key,
            'value': self.get(),
        })

config_head_html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
    <title>Crunchy :: Config</title>
</head>
<body>
"""
config_tail_html = """</body></html>"""
