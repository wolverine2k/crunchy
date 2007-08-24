""" configuration.py:
    Keeps track of user based settings, some automatically set
    by Crunchy, others ajustable by the user.
"""
import cPickle
import os
import sys
from urlparse import urlsplit

import translation
_ = translation._

translation.init_translation()

initial_security_set = False

editarea_languages_allowed_values = ['de', # German
                                     'dk', # Danish
                                     'en', # English
                                     'fr', # French
                                     'hr', # Croatian
                                     'it', # Italian
                                     'ja', # Japanese
                                     'nl', # Dutch
                                     'pl', # Polish
                                     'pt' # Portuguese
                                    ]
languages_allowed_values = ['en', # English
                            'fr' # French
                            ]
security_allowed_values = [
                        'trusted','display trusted',
                        'normal', 'display normal',
                        'strict', 'display strict'
                            ]

# Unfortunately, IPython interferes with Crunchy;
#  I'm commenting it out, keeping it in as a reference.
override_default_interpreter_allowed_values = ['default', # ipython,
        'Borg', 'isolated', 'Human', 'parrot', 'Parrots', 'TypeInfoConsole']

no_markup_allowed_values = ["none", "editor", 'python_tutorial',
                    "python_code", "image_file"]
                                  # image_file needs an optional argument
for interpreter in override_default_interpreter_allowed_values:
    no_markup_allowed_values.append(interpreter)

doc_help_allowed_values = [True, False]
dir_help_allowed_values = [True, False]

class Defaults(object):
    """
    class containing various default values:
        user_dir: home user directory
        temp_dir: temporary (working) directory
        nm: no_markup option, i.e. default mode to use when the user has
            not specied a vlam keyword
        language: language to use for feedback to user - and anything
            else that might have been translated.
        editarea_language: language used for ui of editarea
        friendly: traceback settings
        security: level of filtering of web pages
        doc_help: interactive help for Borg consoles
        dir_help: interactive help for Borg consoles
        my_style: enables preferred styling of Python code, etc.

    This class is instantiated [instance name: defaults] within this module.
    """
    _prefix = "crunchy"

    def __init__(self):
        self.set_dirs()
        self.log_filename = os.path.join(os.path.expanduser("~"), "crunchy_log.html")
        self.load_settings()
        translation.init_translation(self.__language)
        self.logging_uids = {}  # {uid : (name, type)}
                               # name is defined by tutorial writer
                               # type is one of 'interpreter', 'editor',...
        self.log = {} #{name: [ pre.code, input, output, input, output, ...]}
        # backup value used in resetting security level

    def load_settings(self):
        success = False
        pickled_path = os.path.join(self.__user_dir, "settings.pkl")
        try:
            pickled = open(pickled_path, 'rb')
            success = True
        except:
            print "No configuration file found."
        if success:
            saved = cPickle.load(pickled)
            pickled.close()

        try:
            self.__no_markup = saved['no_markup']
        except:
            self.__no_markup = "python_tutorial"
        try:
            self.__language = saved['language']
        except:
            self.__language = 'en'
        try:
            self.__editarea_language = saved['editarea_language']
        except:
            self.__editarea_language = 'en'
        try:
            self.__friendly = saved['friendly']
        except:
            self.__friendly = True
        try:
            self.__local_security = saved['local_security']
        except:
            self.__local_security = 'normal'
        try:
            self.site_security = saved['site_security']
        except:
            self.site_security = {}
        try:
            self.__override_default_interpreter = saved['override_default_interpreter']
        except:
            self.__override_default_interpreter = 'default'
        try:
            self.__doc_help = saved['doc_help']
        except:
            self.__doc_help = True  # ok for beginners
        try:
            self.__dir_help = saved['dir_help']
        except:
            self.__dir_help = False # less useful for beginners
        try:
            self.__my_style = saved['my_style']
        except:
            self.__my_style = False
        try:
            self.styles = saved['styles']
        except:
            self.styles = {}

        if not success:
            # save the file with the default values
            self.save_settings()
        return

    def save_settings(self):
        saved = {}
        saved['no_markup'] = self.__no_markup
        saved['language'] = self.__language
        saved['editarea_language'] = self.__editarea_language
        saved['friendly'] = self.__friendly
        saved['local_security'] = self.__local_security
        saved['override_default_interpreter'] = self.__override_default_interpreter
        saved['doc_help'] = self.__doc_help
        saved['dir_help'] = self.__dir_help
        saved['my_style'] = self.__my_style
        saved['styles'] = self.styles
        saved['site_security'] = self.site_security
        # time to save
        pickled_path = os.path.join(self.__user_dir, "settings.pkl")
        try:
            pickled = open(pickled_path, 'wb')
        except:
            print "could not open file in configuration.save_settings()"
            return
        cPickle.dump(saved, pickled)
        pickled.close()
        print "saved settings"
        return

    def set_dirs(self):
        '''sets the user directory, creating it if needed.
           Creates also a temporary directory'''
        self.__user_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
        # There is no real need to have a separate temp (sub)directory
        self.__temp_dir = self.__user_dir
        if not os.path.exists(self.__user_dir):  # first time ever
            try:
                os.makedirs(self.__user_dir)
                if not os.path.exists(self.__temp_dir):
                    try:
                        os.makedirs(self.__temp_dir)
                    except:
                        # Note: we do not translate diagnostic messages
                        # sent to the terminal
                        print "Created successfully home directory."
                        print "Could not create temporary directory."
                        self.__temp_dir = None
                    return
            except:
                print "Could not create the user directory."
                self.__user_dir = os.getcwd()  # use crunchy's as a default.
                self.__temp_dir = os.path.join(self.__user_dir, "temp")
                if not os.path.exists(self.__temp_dir):
                    try:
                        os.makedirs(self.__temp_dir)
                    except:
                        print "Could not create temporary directory."
                        self.__temp_dir = None
                    return
                return
        # we may encounter a situation where a ".crunchy" directory
        # had been created by an old version without a temporary directory
        if not os.path.exists(self.__temp_dir):
            try:
                os.makedirs(self.__temp_dir)
            except:
                print "home directory '.crunchy' exists; however,"
                print "could not create temporary directory."
                self.__temp_dir = None
            return
        return

    #==============
    def get_user_dir(self):
        return self.__user_dir

    user_dir = property(get_user_dir, None, None,
                       _("(Fixed) User home directory: "))
    #==============

    def get_temp_dir(self):
        return self.__temp_dir.decode(sys.getfilesystemencoding())

    temp_dir = property(get_temp_dir, None, None,
                       _("(Fixed) Temporary working directory: "))

    #==============

    def get_dir_help(self):
        return self.__dir_help

    def set_dir_help(self, choice):
        if choice not in dir_help_allowed_values:
            print _("Invalid choice for %s.dir_help")%self._prefix
            print _("The valid choices are: "), dir_help_allowed_values
            print _("The current value is: "), self.__dir_help
            return
        self.__dir_help = choice
        self.save_settings()
        return

    dir_help = property(get_dir_help, set_dir_help, None,
        _('The choices for dir_help are %s\n')% dir_help_allowed_values +\
        _('  The current value is: '))

    #==============

    def get_doc_help(self):
        return self.__doc_help

    def set_doc_help(self, choice):
        if choice not in doc_help_allowed_values:
            print _("Invalid choice for %s.doc_help")%self._prefix
            print _("The valid choices are: "), doc_help_allowed_values
            print _("The current value is: "), self.__doc_help
            return
        self.__doc_help = choice
        self.save_settings()
        return

    doc_help = property(get_doc_help, set_doc_help, None,
        _('The choices for doc_help are %s\n')% doc_help_allowed_values +\
        _('  The current value is: '))

    #==============

    def get_help(self):
        '''Help message that includes all the values that are set
           as properties.'''
        __help = _("""
You can change some of the default values by Crunchy, just like
you can obtain this help message, using either an interpreter
prompt or an editor, and assigning the desired value to a given
variable.  Some of these variables are "fixed", which means that
their value can not be changed by the user.
-
Here are the values of some variables currently used by Crunchy.
""")
# we sort the keys so that they are listed in alphabetical order,
# making them easier to find when reading the rather long text
        keys = []
        for key in Defaults.__dict__:
            keys.append(key)
        keys.sort()

        for key in keys:
            val = Defaults.__dict__[key]
            if isinstance(val, property):
                if val.__doc__ != 'help':
                    value = val.fget(self)
# we make sure that the choice is shown as a string if expected from the user
                    if value not in [True, False]:
                        try:
                            value = str(value)
                        except:
                            try: # perhaps a path
                                value = str(value.encode(sys.getfilesystemencoding()))
                            except: # or translation
                                try:
                                    value = str(value.encode('utf-8'))
                                except:
                                    value = str(value.encode(sys.getdefaultencoding()))
                        value = "'" + value + "'"
                    else:
                        value = str(value)
                    __help += "\n"  + "~"*50 +"\n" + (val.__doc__) +\
                        self._prefix + "." +  key + " = " + value
        return __help + "\n"

    help = property(get_help, None, None, 'help')
    #==============
    #
    # Crunchy allows the user to treat a bare <pre> as though it had
    # a given vlam value.

    def get_nm(self):
        return self.__no_markup

    def set_nm(self, choice):
        ch = choice.strip().split(' ')
        valid = False
        if ch[0] in no_markup_allowed_values:
            if ch[0] == 'image_file':
                if len(ch) == 2: # valid filename needed, nothing else
                    self.__no_markup = choice
                    valid = True
                else:  # no valid file name
                    pass
            else:
                self.__no_markup = choice
                valid = True
        if not valid:
            print _("Invalid choice for %s.no_markup")%self._prefix
            print _("The valid choices are: "), no_markup_allowed_values
            print _('with "image_file   file_name" as a required option.')
            print _("The current value is: "), self.__no_markup
        else:
            self.save_settings()

    no_markup = property(get_nm, set_nm, None,
        _('The choices for "pre" tag without Crunchy markup are %s\n')% no_markup_allowed_values +\
        _('  The current value is: '))
    #==============

    def get_language(self):
        return self.__language

    def set_language(self, choice):
        if choice in languages_allowed_values:
            self.__language = choice
            translation.init_translation(self.__language)
            print _("language set to: ") , choice
            if choice in editarea_languages_allowed_values:
                self.__editarea_language = choice
                print _("editarea_language also set to: ") , choice
            else:
                print _("Note: while this is a valid choice, this choice is not available for a language provided by editarea. ") +\
                _("The language choice for editarea remains ") +\
                 self.__editarea_language
            self.save_settings()
        else:
            print _("Invalid choice for %s.language")%self._prefix
            print _("The valid choices are: "), languages_allowed_values

    language = property(get_language, set_language, None,
        _('The choices for language are %s\n')% languages_allowed_values +\
        _('  The current value is: '))
    #==============

    def get_editarea_language(self):
        return self.__editarea_language

    def set_editarea_language(self, choice):
        if choice in editarea_languages_allowed_values:
            self.__editarea_language = choice
            print _("editarea_language set to: ") , choice
            self.save_settings()
        else:
            print _("Invalid choice for %s.editarea_language")%self._prefix
            print _("The valid choices are: "), editarea_languages_allowed_values

    editarea_language = property(get_editarea_language, set_editarea_language, None,
        _('The choices for editarea_language are %s\n')% editarea_languages_allowed_values +\
        _('  The current value is: '))
    #==============

    def get_friendly_traceback(self):
        return self.__friendly

    def set_friendly_traceback(self, choice):
        if choice == True:
            self.__friendly = True
            print _("Crunchy will attempt to provide friendly error messages.")
            self.save_settings()
        elif choice == False:
            self.__friendly = False
            print _("Crunchy's error messages will be similar to Python's default tracebacks.")
            self.save_settings()
        else:
            print _("friendly attribute must be set to True or False.")

    friendly = property(get_friendly_traceback, set_friendly_traceback, None,
        _('The choices for friendly tracebacks are %s\n')% [True, False] +\
        _('  The current value is: '))

    #==============

    def get_site_security(self, site):
        if site in self.site_security:
            print "site = ", site
            print "self.site_security = ", self.site_security
            return self.site_security[site]
        else:
            return 'display trusted'

    def set_site_security(self, site, choice):
        if choice in security_allowed_values:
            self.site_security[site] = choice
            self.save_settings()
            print _("site security set to: ") , choice
        else:
            print _("Invalid choice for %s.site_security")%self._prefix
            print _("The valid choices are: "), security_allowed_values

    def get_local_security(self):
        return self.__local_security

    def set_local_security(self, choice):
        if choice in security_allowed_values:
            self.__local_security = choice
            print _("security set to: ") , choice
            self.save_settings()
        else:
            print _("Invalid choice for %s.local_security")%self._prefix
            print _("The valid choices are: "), security_allowed_values

    local_security = property(get_local_security, set_local_security, None,
        _('The choices for local_security levels are %s\n')% security_allowed_values +\
        _('  The current value is: '))
    #==============

    def get_override_default_interpreter(self):
        return self.__override_default_interpreter

    def set_override_default_interpreter(self, choice):
        if choice in override_default_interpreter_allowed_values:
            self.__override_default_interpreter = choice
            print _("override_default_interpreter set to: ") , choice
            self.save_settings()
        else:
            print _("Invalid choice for %s.override_default_interpreter")%self._prefix
            print _("The valid choices are: "), override_default_interpreter_allowed_values

    override_default_interpreter = property(get_override_default_interpreter,
           set_override_default_interpreter, None,
            _('The choices for override_default_interpreter are %s\n')%\
             override_default_interpreter_allowed_values +\
            _('  The current value is: '))

    #==============

    def get_my_style(self):
        return self.__my_style

    def set_my_style(self, choice):
        if choice in [True, False]:
            self.__my_style = choice
            print _("my_style set to: ") , choice
            self.save_settings()
        else:
            print _("Invalid choice for %s.my_style")%self._prefix
            print _("The valid choices are: "), [True, False]

    my_style = property(get_my_style, set_my_style, None,
            _('The choices for my_style are %s\n')%\
             [True, False] +\
            _("If set to True, Crunchy's default styles are replaced"+
              " by the user's choice specified in %s.styles\n")%_prefix +\
            _('\n  The current value for my_style is: '))

    #==============
defaults = Defaults()
