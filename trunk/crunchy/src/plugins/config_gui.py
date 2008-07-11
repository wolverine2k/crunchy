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


def set_config():
    pass
def config_page():
    pass

###############################################################
#### We rely on a ConfigOption class to keep track of an option
#### This is dummy code that will later be integrated into
#### configuration.py

class ConfigOption(object):
    all_options = {}

    def __init__(self, key, initial):
        """
        >>> obj = ConfigOption("test")
        >>> obj.get()
        'test'
        """
        self.key = key
        self.set(initial)
        ConfigOption.all_options[key] = self

    def get(self):
        return self.__value

    def set(self, value):
        self.__value = value

class MultiOption(ConfigOption):
    """An option that has multiple predefined choices
    """
    def __init__(self, key, initial, values):
        super(MultiOption, self).__init__(key, initial)
        self.values = values

    def get_values(self):
        """get the possible values"""
        return self.values

################################################################

class ConfigWidget(object):
    """

    """
    next_id = 0

    def __init__(self, option):
        self.option = option
        self.id = ConfigWidget.next_id
        ConfigWidget.next_id += 1

    def pre_render(self, handle):
        handle.write("<div>")

    def post_render(self, handle):
        handle.write("</div>")

class MultiChoiceWidget(ConfigWidget):
    """
    """
    # if there are les than or equal to this number of values, use a
    # radiobutton group, otherwise use a dropdown box
    threshold = 4
    def __init__(self, option):
        super(MultiChoiceWidget, self).__init__(option)

    def render(self, handle):
        """render the widget to a particular file object"""
        values = self.option.get_values()
        if len(values) <= MultiChoiceWidget.threshold:
            for value in values:
                handle.write('<input type="radio" name="')
                handle.write(self.option.key)
                handle.write('" value="')
                handle.write(value)
                handle.write('" ')
                if value == self.option.get():
                    handle.write('checked="checked" ')
                handle.write(" />")
                handle.write(value + "<br />\n")
                # TODO insert some javasrcipt
        else:
            handle.write('<select name="%s">' % self.option.key)
            # current value first
            handle.write('<option value="%s"> %s' % (self.option.get(), self.option.get()))
            for value in values:
                if value != self.option.get():
                    handle.write('<option value="%s"> %s' % (value, value))
            handle.write("</select>")


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
