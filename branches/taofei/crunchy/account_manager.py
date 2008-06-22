'''Account Manager For Crunchy
'''
import os,sys,md5
from getpass import getpass

pwd_file_path = os.path.join(os.path.dirname(__file__), ".PASSWD")

class Accounts(dict):
    '''Account Mamnager'''

    realm = 'Crunchy Access'

    def __init__(self, pwp):
        self.pwd_file_path = pwp
        try:
            self.load()
        except IOError,e:
            pass

    def load(self):
        data = open(self.pwd_file_path, 'rb').read()
        for line in data.split('\n'):
            if line == "":
                continue
            u,p = line.split(':',1)
            dict.__setitem__(self, u, p)

    def save(self):
        lines = []
        for item in self.items():
            lines.append(':'.join(item))
        data = '\n'.join(lines)
        f = open(self.pwd_file_path, 'w')
        f.write(data)
        f.close()

    def __setitem__(self, key, item): 
        dict.__setitem__(self, key, md5.md5('%s:%s:%s' %(key, self.realm, item)).hexdigest())

class AMCLI(object):
    '''Account Mamnager Command Line Interface'''
   
    def __init__(self):
        self.welcome_msg = "Crunchy Account Manager"
        #print (self.welcome_msg)

    def start(self):
        print (self.welcome_msg)
        self.accounts = Accounts(pwd_file_path)        
        print ("type help for help")
        self.run()

    def run(self):
        while(True):
            command = ""
            try:
                command = raw_input(">>>")
            except EOFError,e:
                print "Please use 'exit' to exit the account manager"
                continue
            if command:
                self.on_command(command)

    def on_command(self, command):
        'command dispatcher'
        command = command.strip().split(" ", 1)
        if hasattr(self, "cmd_" + command[0]):
            if command[0] in ('help', 'list', 'exit'):
                getattr(self, "cmd_" + command[0])()
            elif len(command) > 1:
                getattr(self, "cmd_" + command[0])(command[1])
            else:
                print ("Argument username is need for command %s" %(command[0]))
        else:
            print ("Bad command")

    def cmd_exit(self):
        'exit : exit'
        raise SystemExit

    def cmd_list(self):
        'list : list all users'
        for user in self.accounts:
            print(user)

    def cmd_new(self, username):
        'new <username> : add a new user'
        password = getpass("Please input the password:") 
        if username in self.accounts:
            print ("Error: user %s already exists")
        else:
            self.accounts[username] =  password
            self.accounts.save()

    def cmd_pwd(self, username):
        "pwd <username> : change a user's password"
        password = getpass("Please input the new password:") 
        if username not in self.accounts:
            print ("Error: user %s doesn't exist")
        else:
            self.accounts[username] =  password
            self.accounts.save()

    def cmd_del(self, username):
        "del <username> : delete a user"
        if username not in self.accounts:
            print ("Error: user %s doesn't exist")
        else:
            del self.accounts[username]
            self.accounts.save()

    def cmd_help(self):
        "help : show this message"
        self.help()

    def help(self):
        msg = "Crunchy Account Manager\nsupported commands:\n"
        for attr in dir(self):
            if attr.startswith('cmd_'):
                msg += "  %s\n" %(getattr(self, attr).__doc__)
        print (msg)


        
class AMGUI:
    pass


def get_accounts(path = None):
    if path is None:
        path = pwd_file_path
    return Accounts(pwd_file_path)

def check_for_password_file(path = None):
    if path is None:
        path = pwd_file_path
    if not os.path.exists(path):
        print("Password file not exisi, please create one using the accout manager")
        return False
    else:
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        pwd_file_path = sys.argv[1]
    am = AMCLI()
    am.start()

