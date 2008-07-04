""" configuration.py:
    Keeps track of user based settings, some automatically set
    by Crunchy, others ajustable by the user.
"""

### Important:
#
# In order to reduce the list of variables displayed in the popup
# "tooltip" when the user enters "crunchy.", most methods have been
# prefixed by a leading underscore; Crunchy (in tooltip.py) filters
# out such methods from the display.

import os
from urlparse import urlsplit


from src.interface import config, u_print, translate, python_version, debug
# the following is needed for unit tests, since debug_flag is normally
# set when crunchy is started.
try:
    from src.interface import debug_flag
except:
    debug_flag = False

if python_version < 3:
    import cPickle
else:
    print("Python 3.x not supported")
    raise SystemExit
    #import pickle as cPickle

ANY = '*'

_ = translate['_']
translate['init_translation']()

# Existing translations for Crunchy messages
trans_path = os.path.join(config['crunchy_base_dir'], "translations")
# allow values like "en" or "en_GB"
languages_allowed_values = [f for f in os.listdir(trans_path)
                             if (len(f)==2 or (len(f) == 5 and f[2] == '_'))
                                    and not f.startswith('.')]
# Existing translations for editarea
trans_path2 = os.path.join(config['crunchy_base_dir'], "server_root", "edit_area", "langs")
# language file names end in ".js"
editarea_languages_allowed_values = [f[0:-3] for f in os.listdir(trans_path)
                             if (len(f)==5 or (len(f) == 8 and f[2] == '_'))
                                    and not f.startswith('.')]

security_allowed_values = [
                        'trusted','display trusted',
                        'normal', 'display normal',
                        'strict', 'display strict'
                            ]

# Unfortunately, IPython interferes with Crunchy;
#  I'm commenting it out, keeping it in as a reference.
override_default_interpreter_allowed_values = ['default', # ipython,
        'interpreter', 'Borg', 'isolated', 'Human', 'parrot', 'Parrots', 'TypeInfoConsole']

no_markup_allowed_values = ["none", "editor", 'python_tutorial',
            "python_code", "doctest", "alternate_python_version", "alt_py"]

for interpreter in override_default_interpreter_allowed_values:
    no_markup_allowed_values.append(interpreter)



forward_accept_language_allowed_values = [True, False]

def make_property(name, allowed, default=None):
    '''creates properties within allowed values with some defaults,
       and enables automatic saving of new values'''
    if default is None:
        default = allowed[0]

    def fget(obj):
        return getattr(obj, "_"+name)

    def fset(obj, val):
        '''assigns a value if allowed, and saves the result'''
        prefs = getattr(obj, "prefs")
        if ANY in allowed and val != ANY:
            allowed.append(val)
        if val not in allowed:
            try:
                current = getattr(obj, "_"+name) # can raise AttributeError
                                                   # if not (yet) defined...
                u_print(_("Invalid choice for %s.%s") % (prefs['_prefix'], name))
                u_print(_("The valid choices are: "), allowed)
                u_print(_("The current value is: "), current)
            except AttributeError: # first time; set to default!
                setattr(obj, "_"+name, default)
                getattr(obj, '_save_settings')(name, default, initial=True)
        elif val != ANY:
            try:  # don't save needlessly if there is no change
                current = getattr(obj, "_"+name)
                if val == current:
                    return
                else:
                    setattr(obj, "_"+name, val)
                    getattr(obj, '_save_settings')(name, val)
            except:
                setattr(obj, "_"+name, val)
                getattr(obj, '_save_settings')(name, val)
        return
    return property(fget, fset)

class Base(object):
    '''Base class for all objects that keeps track of
       configuration values in properties.  On its own, it does nothing;
       see test_configuration.rst for sample uses.'''

    def init_properties(self, cls):
        '''automatically assigns all known properties, keeping track of
        them in a dict.'''
        # Note: properties are class variables which is why we need
        # to pass the class name as a parameter.
        keys = []
        for key in cls.__dict__:
            keys.append(key)
            val = cls.__dict__[key]
            if isinstance(val, property):
                val.fset(self, ANY)
        return

    def _save_settings(self, name, value, initial=False):
        raise NotImplementedError


class Defaults(Base):
    """
    class containing various default values:
        dir_help: interactive help for Borg consoles
        doc_help: interactive help for Borg consoles
        forward_accept_language: respecting user's webbrowser's language option
                                 settings
        friendly: traceback settings
        user_dir: home user directory
        temp_dir: temporary (working) directory
        nm: no_markup option, i.e. default mode to use when the user has
            not specied a vlam keyword
        language: language to use for feedback to user - and anything
            else that might have been translated.
        editarea_language: language used for ui of editarea

        security: level of filtering of web pages

        my_style: enables preferred styling of Python code, etc.
        alternate_python_version: path of an alternate Python interpreter

    This class is instantiated [instance name: defaults] within this module.
    """
    def __init__(self, prefs):
        self.site_security = {}
        self.prefs = prefs
        self.prefs.update( {'_prefix': 'crunchy',
                            'page_security_level': self.page_security_level,
                            '_set_site_security': self._set_site_security,
                            'site_security': self.site_security})
        self._set_dirs()
        # self.logging_uids is needed by comitIO.py:87
        self.logging_uids = {}  # {uid : (name, type)}
                               # name is defined by tutorial writer
                               # type is one of 'interpreter', 'editor',...
        self.init_properties(Defaults)

    browser_choices =  make_property('browser_choices', ['None', 'python',
                                        'rst', 'local_html', 'remote_html'])
    dir_help = make_property('dir_help', [True, False])
    doc_help = make_property('doc_help', [True, False])
    forward_accept_language = make_property('forward_accept_language',
                                            [True, False])
    friendly = make_property('friendly', [True, False])
    _trans_path = os.path.join(config['crunchy_base_dir'], "translations")
    override_default_interpreter = make_property('override_default_interpreter',
                                    override_default_interpreter_allowed_values)
    language = make_property('language',
                            [f for f in os.listdir(_trans_path)
                             # allow values like "en" or "en_GB"
                             if (len(f)==2 or (len(f) == 5 and f[2] == '_'))
                                    and not f.startswith('.')],
                           default='en')
    editarea_language = make_property('editarea_language',
                                      [f[0:-3] for f in os.listdir(trans_path)
                             if (len(f)==5 or (len(f) == 8 and f[2] == '_'))
                                    and not f.startswith('.')])
    local_security = make_property('local_security', ['trusted',
                        'display trusted', 'normal', 'display normal',
                        'strict', 'display strict'])
    no_markup = make_property('no_markup', no_markup_allowed_values)

    power_browser = make_property('power_browser', ['None', 'python', 'rst',
                                                'local_html', 'remote_html'])
    my_style = make_property('my_style', [False, True])
    alternate_python_version = make_property('alternate_python_version', ['*'])


    def _set_dirs(self): # "tested"; i.e. called in unit tests.
        '''sets the user directory, creating it if needed.
           Creates also a temporary directory'''
        home = os.path.expanduser("~")
        self.__user_dir = os.path.join(home, ".crunchy")
        self.__temp_dir = os.path.join(home, ".crunchy", "temp")

        # hack to make it work for now.
        self.user_dir = self.__user_dir
        self.temp_dir = self.__temp_dir

        if not os.path.exists(self.__user_dir):  # first time ever
            try:
                os.makedirs(self.__user_dir)
                if not os.path.exists(self.__temp_dir):
                    try:
                        os.makedirs(self.__temp_dir)
                    except:
                        # Note: we do not translate diagnostic messages
                        # sent to the terminal
                        u_print("Created successfully home directory.")
                        u_print("Could not create temporary directory.")
                        self.__temp_dir = self.__user_dir
                    return
            except:
                u_print("Could not create the user directory.")
                self.__user_dir = os.getcwd()  # use crunchy's as a default.
                self.__temp_dir = os.path.join(self.__user_dir, "temp")
                if not os.path.exists(self.__temp_dir):
                    try:
                        os.makedirs(self.__temp_dir)
                    except:
                        u_print("Could not create temporary directory.")
                        self.__temp_dir = self.__user_dir
                    return
                return
        # we may encounter a situation where a ".crunchy" directory
        # had been created by an old version without a temporary directory
        if not os.path.exists(self.__temp_dir):
            try:
                os.makedirs(self.__temp_dir)
            except:
                u_print("home directory '.crunchy' exists; however, ")
                u_print("could not create temporary directory.")
                self.__temp_dir = self.__user_dir
            return
        return

    def _save_settings(self, name, value, initial=False):
        if not initial:
            print "Setting", name, '=', value
        self.prefs[name] = value

    def page_security_level(self, url):
        info = urlsplit(url)
        # info.netloc == info[1] is not Python 2.4 compatible; we "fake it"
        info_netloc = info[1]
        if info_netloc == '':
            level = self.local_security
        else:
            level = self._get_site_security(info_netloc)
        self.current_page_security_level = level
        return level

    def _get_site_security(self, site):
        if site in self.site_security:
            #u_print("site = ", site)
            #u_print("self.site_security = ", str(self.site_security))
            return self.site_security[site]
        else:
            return 'display trusted'

    def _set_site_security(self, site, choice):
        if choice in security_allowed_values:
            self.site_security[site] = choice
            self._save_settings()
            u_print(_("site security set to: ") , choice)
        else:
            u_print((_("Invalid choice for %s.site_security")%self._prefix))
            u_print(_("The valid choices are: "), str(security_allowed_values))

    user_dir = make_property('user_dir', [ANY])
    temp_dir = make_property('temp_dir', [ANY])

    #==============

defaults = Defaults(config)

# the following may be set as an option when starting Crunchy
if 'initial_security_set' not in config:
    config['initial_security_set'] = False

#import pprint
#pprint.pprint(config)