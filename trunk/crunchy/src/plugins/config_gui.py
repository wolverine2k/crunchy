"""
config_gui.py : a plugin to enable users to configure crunchy nicely.

"""

from src.interface import plugin

provides = set(["/comet", "/input"])

def register():  # tested
    '''registers two http handlers: /config and /set_config'''
    plugin['register_http_handler'](
                    "/set_config%s" % plugin['session_random_id'], set_config)
    plugin['register_http_handler']("/config", config_page)



class ConfigOption(object):     # tested
    all_options = {}
    
    def __init__(self, key, initial):       # tested
        """
        """
        self.key = key
        self.set(initial)
        ConfigOption.all_options[key] = self
        
    def get(self):      # tested
        return self.__value
        
    def set(self, value):   # tested
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
        handle.write("<div>\n")
        if len(values) <= MultiOption.threshold:
            for value in values:
                handle.write('<input type="radio" name="')
                handle.write(self.key)
                handle.write('" value="')
                handle.write(value)
                handle.write('" ')
                if value == self.get():
                    handle.write('checked="checked" ')
                handle.write(" />")
                handle.write(value + "<br />\n")
                # TODO insert some javasrcipt
        else:
            handle.write('<select name="%s">' % self.key)
            # current value first
            handle.write('<option value="%s"> %s' % (self.get(), self.get()))
            for value in values:
                if value != self.get():
                    handle.write('<option value="%s"> %s' % (value, value))
            handle.write("</select>")
        handle.write("</div>")
