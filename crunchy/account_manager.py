'''Account Manager For Crunchy
'''
import os,sys,md5
from getpass import getpass

pwd_file_path = os.path.join(os.path.dirname(__file__), ".PASSWD")

class Accounts(dict):
    '''Account Mamnager'''

    realm = 'Crunchy Access'

    separator = '|'

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
            u,hd,p = line.split(self.separator, 2)
            dict.__setitem__(self, u, (hd,p))

    def save(self):
        lines = []
        for key, value in self.items():
            lines.append(self.separator.join([key, value[0], value[1]]))
        data = '\n'.join(lines)
        f = open(self.pwd_file_path, 'w')
        f.write(data)
        f.close()

    def __setitem__(self, key, item): 
        home = item[0]
        password = md5.md5('%s:%s:%s' %(key, self.realm, item[1])).hexdigest()
        dict.__setitem__(self, key, (home, password))

    def get_password(self, key, default = ""):
        if key not in self:
            return default
        else:
            return self[key][1]


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
            if command[0] in ('list', 'exit'):
                getattr(self, "cmd_" + command[0])()
            elif len(command) > 1:
                getattr(self, "cmd_" + command[0])(command[1])
            elif command[0] == 'help':
                getattr(self, "cmd_" + command[0])()
            else:
                print ("Argument username is need for command %s" %(command[0]))
        else:
            print ("Bad command")

    def cmd_exit(self):
        'exit : exit'
        raise SystemExit

    def cmd_list(self):
        'list : list all users'
        print ("%s\t%s" %("username", "home direcotry"))
        print ('---------------------------------------')
        for user in self.accounts:
            print ("%s\t\t%s" %(user, self.accounts[user][0]))

    def cmd_new(self, username):
        'new <username> : add a new user'
        home = raw_input("Please input the home directory:") 
        while True:
            password = getpass("Please input the password:") 
            password2 = getpass("Please input the password again:") 
            if password == password2:
                break
            else:
                print("Password don't match, please try again.")
        if username in self.accounts:
            print ("Error: user %s already exists" %(username))
        else:
            self.accounts[username] =  (home, password)
            self.accounts.save()

    def cmd_edit(self, username):
        "edit <username> : change a user's home direcotry and password"
        if username not in self.accounts:
            print ("Error: user %s doesn't exist" %(username))
        else:
            home = raw_input("Please input the new home directory:[%s]" %(self.accounts[username][0]))
            if not home:
                home = self.accounts[username][0]
            while True:
                password = getpass("Please input the new password:") 
                password2 = getpass("Please input the password again:") 
                if password == password2:
                    break
                else:
                    print("Password don't match, please try again.")
            self.accounts[username] =  (home, password)
            self.accounts.save()

    def cmd_del(self, username):
        "del <username> : delete a user"
        if username not in self.accounts:
            print ("Error: user %s doesn't exist")
        else:
            del self.accounts[username]
            self.accounts.save()

    def cmd_load(self, file_name):
        '''load <file_name> : load accounts from file <file_name>
        File format :
        user1 home1 pass1
        user2 home2 pass2
        ....
        you can user '\\t' , space , or ',' as seperator 
        '''
        f = open(file_name)
        lines = f.readlines()
        try_sep = ('\t', ' ', ',');
        for sep in try_sep:
            data = []
            is_ok = True
            for line in lines:
                t = line.split(sep)
                if len(t) != 3:
                    is_ok = False
                    break
                else:
                    data.append(t)
            if is_ok:
                break
        else:
            print("Error: Can't parse input file %s" %file_name)
        for t in data:
            self.accounts[t[0]] = t[1:]
        self.accounts.save()
        print("%d accounts loaded." %(len(data)))

    def cmd_help(self, topic = None):
        "help [<help_topic>]: display this message or display help of <help_topic>"
        self.help(topic)

    def help(self, topic = None):
        if topic is None:
            msg = "Crunchy Account Manager\nsupported commands:\n"
            for attr in dir(self):
                if attr.startswith('cmd_'):
                    msg += "  %s\n" %(getattr(self, attr).__doc__.split('\n')[0])
            print (msg)
        else:
            if hasattr(self, 'cmd_' + topic):
                print(getattr(self, 'cmd_' + topic).__doc__ + '\n')
            else:
                print("No such command %s" %topic)
        
def get_accounts(path = None):
    if path is None:
        path = pwd_file_path
    return Accounts(pwd_file_path)

def check_for_password_file(path = None):
    if path is None:
        path = pwd_file_path
    if not os.path.exists(path):
        print("Password file not exist, please create one using the accout manager")
        return False
    else:
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        pwd_file_path = sys.argv[1]
    am = AMCLI()
    am.start()

