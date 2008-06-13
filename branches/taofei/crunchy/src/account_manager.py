'''Account Manager For Crunchy
'''
import os

pwd_file_path = os.path.join(os.path.dirname(__file__), "..", ".crunchypass")


class AccountManager(dict):
    '''Account Mamnager'''

    def __init__(self, pwp = pwd_file_path, key = None):
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

    pass


class AMGUI:
    pass


accounts = AccountManager()

if __name__ == '__main__':
   accounts.add('crunchy','password')


