'''Account Manager For Crunchy
'''
import os,sys
from getpass import getpass

pwd_file_path = os.path.join(os.path.dirname(__file__), ".PASSWD")


class Accounts(dict):
    '''Account Mamnager'''

    def __init__(self, pwp, key = None):
        self.pwd_file_path = pwp
        self.key = key
        try:
            self.load()
        except IOError,e:
            pass

    def load(self):
        data = open(self.pwd_file_path, 'rb').read()
        data = self.decrypt(data)
        for line in data.split('\n'):
            if line == "":
                continue
            u,p = line.split(':',1)
            self[u] = p

    def save(self):
        lines = []
        for item in self.items():
            lines.append(':'.join(item))
        data = self.encrypt('\n'.join(lines))
        f = open(self.pwd_file_path, 'w')
        f.write(data)
        f.close()

    def add(self, username, password):
        self[username] = password
        self.save()

    def encrypt(self, data):
        #TODO: using a real algorithm
        return data

    def decrypt(self, data):
        #TODO: using a real algorithm
        return data


class AMCLI(object):
    '''Account Mamnager Command Line Interface'''
   
    def __init__(self):
        self.welcome_msg = "Crunchy Account Manager\n"
        #print (self.welcome_msg)

    def start(self, master_password = None):
        if not master_password:
            print (self.welcome_msg)
            master_password = getpass("Please input the master password:") 
        self.accounts = Accounts(pwd_file_path, master_password)        
        #print ("Password file loaded.")
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


def get_accounts(master_password = None):
    if not master_password:
        master_password = getpass("Please input the master password:") 
        #There is some problme with getpass 
    return Accounts(pwd_file_path, master_password)

if __name__ == '__main__':
    am = AMCLI()
    am.start()

