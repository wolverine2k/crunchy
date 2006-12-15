"""settings.py:
    Keeps track of settings on a per installation basis.
    In future we should expand to some kind of per-user basis.
    Also provides a GUI for changing the settings.
"""

from ConfigParser import SafeConfigParser

class Singleton(object):
    _me = None
    def __new__(cls, *args, **kwargs):
        if cls._me:
            return cls._me
        else:
            cls._me = object.__new__(cls, *args, **kwargs)
            return cls._me

class GlobalUserSettings(Singleton):
    """Holds setting on a per-user, per-installation basis, has methods
    for saving and loading settings.
    Implemented as a class so that in future it will be easier to move to 
    a multi-user system, when we do so we will have to take away the singleton
    superclass.
    
    Settings are saved
    Instance variables are:
        lang: the current language
        
        [add more here as the program develops...]
    """
    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.read("crunchy.cfg")
        self.load()
    
    def load(self):
        try:
            self.lang = self.parser.get("crunchy", "lang")
        except:
            self.lang = "en"
        pass
    
    def save(self):
        try:
            self.parser.add_section("crunchy")
        except:
            pass
        self.parser.set("crunchy", "lang", self.lang)
        self.parser.write(open("crunchy.cfg", 'w'))
