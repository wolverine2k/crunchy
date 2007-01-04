""" configuration.py:
    Keeps track of user preferences.
    In future we should provides a GUI for changing the preferences.
"""

import os
from ConfigParser import SafeConfigParser
from element_tree import HTMLTreeBuilder
import translation

class Borg(object):
    """From the 2nd edition of the Python cookbook.
       Ensures that all instances share the same state and behaviour.
    """
    _shared_state={}
    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj
    
class UserPreferences(Borg):
    """Keeps track of user preferences such as:
    language: the preferred language;
    working_dir: the directory where user-created Python files are saved;
    style: the preferred css style.
    Eventually, more options (e.g. styling of Python programs) will be added.
    """
    __initialised = False
    _language = None
    def __init__(self, root_dir=None):
        if not self.__initialised:
            self.__initialised = True
            self.root_dir = root_dir
            translation.home = root_dir
            self.styles = []
            self.menu = None
            self.config = SafeConfigParser()
            self.changed = False
            self.user_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
            if not os.path.exists(self.user_dir):  # first time ever
                self.create_path()
            self.user_file = os.path.join(self.user_dir, "crunchy.cfg")
            self.load()
        return
    
    def create_path(self):
        '''Creates a path for Crunchy when none exists.'''
        try:
            os.makedirs(self.user_dir)
        except:
            print "Could not create the user directory."
            self.user_dir = os.getcwd()  # use crunchy's a a default.
        return
    
    def create_file(self):
        '''Creates a configuration file when none exist.'''
        self.config.add_section('preferences')
        self.set_language('en')
        self.set_working_dir(self.user_dir)
        self.set_style('gradient1.css')
        f = open(self.user_file, 'w')
        self.config.write(f)
        f.close()
        return
    
    def set_preference(self, option, value):
        '''Set an individual preference option'''
        self.config.set('preferences', option, value)
        self.changed = True
        return
    
    def load(self):
        '''Reads the configuration values and sets them for this session'''
        try:
            self.config.readfp(open(self.user_file, 'r'))
        except:
            self.create_file()
        self.working_dir = self.config.get('preferences', 'working directory')
        self.style = self.config.get('preferences', 'style')
        self.language = self.config.get('preferences', 'language')
        self.changed = False
        return
    
    def save(self):
        '''If necessary, saves the changed values.'''
        if self.changed:
            f = open(self.user_file, 'w')
            self.config.write(f)
            f.close()
            self.changed = False
        return
    
    #== the following are implemented as properties for transparent access

    def get_working_dir(self):
        return self._working_dir

    def set_working_dir(self, path):
        self._working_dir = path
        self.set_preference('working directory', path)
        return

    def get_language(self):
        return self._language

    def set_language(self, lang):
        if self._language is not None:
            if self._language == lang:
                return
            else:
                self.changed = True
        self._language = lang
        self.set_preference('language', lang)
        # make sure we set it first in module translation as it has more
        # choices for editarea
        translation.select(self._language)
        self._editarea_lang = translation.get_editarea_lang()
        
        # more limited choices here.
        if self._language == "fr":
            self.home = "index_fr.html"
            self.options = "src/html/options_fr.html"
        else: # English is the default
            self.home = "index.html"
            self.options = "src/html/options.html"
            self._language = "en"
        self.extract_menu()
        self.save()
        return

    def get_style(self):
        return self._style

    def set_style(self, style):
        self._style = style
        self.set_preference('style', style)
        return
    
    working_dir = property(get_working_dir, set_working_dir)
    language = property(get_language, set_language)
    style = property(get_style, set_style)

    def extract_menu(self):
        filename = os.path.normpath(os.path.join(self.root_dir, self.home))
        try:
            tree = HTMLTreeBuilder.parse(filename)
        except Exception, info:
            print info
        head = tree.find("head")
        body = tree.find("body")
        self.menu = body.find(".//div")
        for link in head.findall('.//link'):
            self.styles.append(link)
        body.clear()
        head.clear()
        body.insert(0, self.menu)
        for link in self.styles:
            head.insert(0, link)
        return
