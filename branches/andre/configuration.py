""" configuration.py:
    Keeps track of user based settings, some automatically set
    by Crunchy, others ajustable by the user.
    In future we should provide a GUI for changing the preferences.
"""
import os

no_markup_allowed_valued = ["none", "editor", "interpreter", "python_code"]

class Defaults(object):
    """
    class containing various default values:
        user_dir: home user directory
        temp_dir: temporary (working) directory

    This class is instantiated [instance name: defaults] within this module.
    """

    def __init__(self):
        self.set_dirs()
        self._prefix = "_crunchy_"
        self.__no_markup = "interpreter"

    def set_dirs(self):
        '''sets the user directory, creating it if needed.
           Creates also a temporary directory'''
        self.__user_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
        self.__temp_dir = os.path.join(self.__user_dir, "temp")
        if not os.path.exists(self.__user_dir):  # first time ever
            try:
                os.makedirs(self.__user_dir)
                try:
                    os.makedirs(self.__temp_dir)
                except:
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
                       "(Fixed) User home directory: ")
    #==============

    def get_temp_dir(self):
        return self.__temp_dir

    temp_dir = property(get_temp_dir, None, None,
                       "(Fixed) Temporary working directory: ")
    #==============

    def get_help(self):
        '''Help message that includes all the values that are set
           as properties.'''
        __help = """
You can change some of the default values by Crunchy, just like
you can obtain this help message, using either an interpreter
prompt or an editor, and assigning the desired value to a given
variable.  Some of these variables are "fixed", which means that
their value can not be changed by the user.
-
Here are the values of some variables currently used by Crunchy.
---------------------------------------------------------------
"""
        for k, v in Defaults.__dict__.iteritems():
            if isinstance(v, property):
                if v.__doc__ != 'help':
                    __help += "\n" + v.__doc__ + self._prefix + "." + k \
                             + " = '" + str(v.fget(self)) + "'"
        return __help + "\n-\n"

    help = property(get_help, None, None, 'help')
    #==============
    #
    # Crunchy allows the user to treat a bare <pre> as though it had
    # a given vlam value.

    def get_nm(self):
        return self.__no_markup

    def set_nm(self, choice):
        if choice in no_markup_allowed_valued:
            self.__no_markup = choice
        else:
            print "Invalid choice for %s.no_markup"%self._prefix
            print "The valid choices are: ", no_markup_allowed_valued
            print "The current value is: ", self.__no_markup

    no_markup = property(get_nm, set_nm, None,
        'The choices for "pre" tag without markup'+\
        ' are %s\nThe current value is: '% no_markup_allowed_valued)
    #==============

defaults = Defaults()
