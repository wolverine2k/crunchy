""" configuration.py:
    Keeps track of user based settings, some automatically set
    by Crunchy, others ajustable by the user.
    In future we should provide a GUI for changing the preferences.
"""
import os
import sys

import translation

_ = translation._

translation.init_translation()

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


no_markup_allowed_values = ["none", "editor", "interpreter", "python_code",
                    "image_file"]  # image_file needs an optional argument

class Defaults(object):
    """
    class containing various default values:
        user_dir: home user directory
        temp_dir: temporary (working) directory

    This class is instantiated [instance name: defaults] within this module.
    """

    def __init__(self):
        self.set_dirs()
        self.log_filename = os.path.join(os.path.expanduser("~"), "crunchy_log.html")
        self._prefix = "crunchy"
        self.__no_markup = "interpreter"
        self.__language = 'en'
        self.__editarea_language = 'en'
        translation.init_translation(self.__language)
        self.logging_uids = {}  # {uid : (name, type)}
                               # name is defined by tutorial writer
                               # type is one of 'interpreter', 'editor',...
        self.log = {} #{name: [ pre.code, input, output, input, output, ...]}

    def set_dirs(self):
        '''sets the user directory, creating it if needed.
           Creates also a temporary directory'''
        self.__user_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
        self.__temp_dir = os.path.join(self.__user_dir, "temp")
        print "creating temp directory", self.__temp_dir
        if not os.path.exists(self.__user_dir):  # first time ever
            try:
                os.makedirs(self.__user_dir)
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
---------------------------------------------------------------
""")
        for k, v in Defaults.__dict__.iteritems():
            if isinstance(v, property):
                if v.__doc__ != 'help':
                    __help += "\n" + v.__doc__ + self._prefix + "." + k \
                             + " = '" + str(v.fget(self)) + "'"
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
            print _('or "image_file   file_name"')
            print _("The current value is: "), self.__no_markup

    no_markup = property(get_nm, set_nm, None,
        _('  The choices for "pre" tag without markup are %s\n  ')% no_markup_allowed_values +\
        _('This has no effect on pages containing any Crunchy markup.\n') +\
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
        else:
            print _("Invalid choice for %s.language")%self._prefix
            print _("The valid choices are: "), languages_allowed_values

    language = property(get_language, set_language, None,
             _('language (two-letter code) used by Crunchy: '))
    #==============

    def get_editarea_language(self):
        return self.__editarea_language

    def set_editarea_language(self, choice):
        if choice in editarea_languages_allowed_values:
            self.__editarea_language = choice
            print _("editarea_language set to: ") , choice
        else:
            print _("Invalid choice for %s.editarea_language")%self._prefix
            print _("The valid choices are: "), editarea_languages_allowed_values

    editarea_language = property(get_editarea_language, set_editarea_language, None,
             _('editor "editarea" language (two-letter code) used by Crunchy: '))
    #==============

defaults = Defaults()
