'''Account Manager For Crunchy
'''

import cmd
import codecs
import os
import sys
from getpass import getpass

# The md5 module is deprecated in 2.5 and then removed in 3.0.
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), ".PASSWD")

class Accounts(dict): # tested
    '''dict-derived class to store user's account information.'''

    realm = 'Crunchy Access'
    separator = '|'

    def __init__(self, pwp=None, from_AMCLI=False): # tested
        if pwp is None:  # use this to allow redefining DEFAULT_PATH
            pwp = DEFAULT_PATH # from outside this module
        self.pwd_file_path = pwp
        self.base_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
        if os.path.exists(pwp):
            try:
                self.load()
            except IOError:
                print("WARNING: Could not open existing password file.")
        else:
            if from_AMCLI:
                print("New password file [path = %s] will be created." % pwp)

    def __setitem__(self, username, item): # tested indirectly
        '''overrides base class dict method so that the password gets
        automatically encrypted.'''
        home = item[0]
        admin_rights = item[2]
        password = '%s:%s:%s' % (username, self.realm, item[1])

        # Python 3: md5() does not take unicode strings.
        if isinstance(password, unicode):
            password = password.encode('utf8')

        encoded_password = md5(password).hexdigest()
        dict.__setitem__(self, username, (home, encoded_password, admin_rights))

    def load(self): # tested indirectly
        '''loads data from password file'''
        for line in codecs.open(self.pwd_file_path, 'r', encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            username, user_dir, encoded_password, admin_rights = line.split(
                                                            self.separator)
            dict.__setitem__(self, username, (user_dir, encoded_password,
                                              admin_rights))

    def save(self): # tested
        '''saves the account information in a file.'''
        lines = []
        for key, value in list(self.items()):
            lines.append(self.separator.join((key,) + value))
        data = '\n'.join(lines)

        f = codecs.open(self.pwd_file_path, 'w', encoding='utf-8')
        f.write(data)
        f.close()

    def get_password(self, username): # tested
        '''given a username, return the corresponding password, if it is a
           known username, otherwise returns an empty string.'''
        if username not in self:
            return ""
        else:
            return self[username][1]

    def get_home_dir(self, username): # tested
        '''given a username, return the corresponding home directory
           if it is a known username, otherwise returns an empty string.'''
        if username not in self:
            return ""
        else:
            return self[username][0]

    def is_admin(self, username):
        '''given a username, indicates whether or not the corresponding
           user has administrative privileges (required to exit crunchy).'''
        if username not in self:
            return False

        return self[username][2] == 'y'

class AMCLI(cmd.Cmd):
    '''Account Manager Command Line Interface'''

    def __init__(self, pwp=None):
        cmd.Cmd.__init__(self)

        # Allows values besides DEFAULT_PATH, for use outside this module.
        if pwp is None:
            pwp = DEFAULT_PATH

        self.intro = "Crunchy's Account Manager.\nFor information, type help.\n"
        self.prompt = "\n>>> "
        self.accounts = Accounts(pwp)
        self.cmdloop()

    def emptyline(self):
        '''Nothing entered. cmd.Cmd wants to repeat the last command,
        which is not what we want.'''

        pass

    def do_set_base_dir(self, args):
        '''set_base_dir : sets the base directory from which accounts are
           created when choosing 'default' or simply pressing enter.'''

        print("The current base directory is %s" % self.accounts.base_dir)
        print("If you want to keep the same base directory, simply press 'enter'.")
        base_dir = raw_input("Please enter the new base directory: ")
        if base_dir != "":
            self.accounts.base_dir = base_dir
            print("The account information for 'username' will be saved in ")
            print(os.path.join(self.accounts.base_dir, 'username'))
        return

    def do_help(self, args):
        '''help : prints a list of available commands'''

        cmd.Cmd.do_help(self, args)

    def do_exit(self, args):
        '''exit : exit the program (accounts are saved automatically)'''

        raise SystemExit

    def do_EOF(self, args):
        '''ctrl-d : exit the program (accounts are saved automatically)'''

        print()
        raise SystemExit

    def do_list(self, args):
        '''list : list all users'''

        print("%s\t%s\t%s" % ("username", "home directory", "admin rights"))
        print('-----------------------------------------------------------')
        for user in self.accounts:
            print("%s\t\t%s\t\t%s" % (user, self.accounts[user][0],
                                                        self.accounts[user][2]))

    def do_new(self, username):
        '''new <username> : add a new user. (ascii characters ONLY)'''

        if username in self.accounts:
            print("Error: user \"%s\" already exists" % username)
            return

        home = raw_input("Please input the home directory [or press 'enter' for default]: ")
        while True:
            password = getpass("Please input the password: ")
            password2 = getpass("Please input the password again: ")
            if password == password2:
                break
            else:
                print("The passwords do not match; please try again.")

        admin_rights = raw_input(
                "Does this user have administrative rights [y or N]? ")
        home = self.evaluate_home(username, home)
        self.accounts[username] = home, password, admin_rights
        self.accounts.save()

    def do_edit(self, username):
        '''edit <username> : change a user's home directory and password.'''

        if username not in self.accounts:
            print("Error: user \"%s\" doesn't exist" % (username))
            return

        home = raw_input("Please input the new home directory [%s]: " %
                         self.accounts[username][0])
        if not home:
            home = self.accounts[username][0]
        else:
            home = self.evaluate_home(username, home)
        while True:
            password = getpass("Please input the new password:")
            password2 = getpass("Please input the password again:")
            if password == password2:
                break
            else:
                print("Password don't match, please try again.")
        admin_rights = raw_input(
                    "Does this user have administrative rights [y or n]? ")
        self.accounts[username] = home, password, admin_rights
        self.accounts.save()

    def do_del(self, username):
        '''del <username> : delete a user'''

        if username not in self.accounts:
            print("Error: user \"%s\" doesn't exist" % username)

        del self.accounts[username]
        self.accounts.save()

    def do_load(self, file_name):
        '''load <file_name> : create accounts from plain file <file_name>
                File format :
                    username_1 home_directory1 password1 admin_rights1
                    username_2 home_directory2 password2 admin_rights2
                    ...
                You can use a single space [' '], a comma [','], or
                a tab character ['\\t'] as separator between values.'''

        if not file_name:
            print("No argument for file name passed to the load command")
            return

        f = codecs.open(file_name, encoding='utf-8')
        lines = f.readlines()
        f.close()

        try_sep = '\t', ' ', ','
        data = []
        for sep in try_sep:
            for line in lines:
                t = line.strip().split(sep)
                if len(t) == 4:
                    data.append(t)
                else:
                    break

            if data:
                break
        else:
            print("Error: Can't parse input file %s" % file_name)

        for t in data:
            self.accounts[t[0]] = t[1:]

        self.accounts.save()
        print("%d accounts loaded." % len(data))

    def evaluate_home(self, username, home):
        '''processes home directory as provided by user to replace
        "shortcuts" by their true values.'''

        if home == "default" or home == '':
            return os.path.join(self.accounts.base_dir, username)
        else:
            return home

if __name__ == '__main__':
    # Gives cmd.Cmd history, Emacs keybindings, and other readline
    # features.
    try:
        import readline
    except ImportError:
        pass

    try:
        if len(sys.argv) > 1:
            pw_file_path = sys.argv[1]
            am = AMCLI(pw_file_path)
        else:
            am = AMCLI()
    except KeyboardInterrupt:
        print()
        raise SystemExit()
