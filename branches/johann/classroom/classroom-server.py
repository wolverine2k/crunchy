"""Classroom server for crunchy"""

from DocXMLRPCServer import DocXMLRPCServer, DocXMLRPCRequestHandler
from elementtree import ElementTree
et = ElementTree
import types
from StringIO import StringIO
from constants import *
from random import random

class InvalidLogin(Exception):
    pass

class UnameInUse(Exception):
    pass

class AccessRecord(object):
    """keeps track of what a particular logon can access"""
    def __init__(self, root, username):
        self.isRoot = root
        self.userName = username
        
class AccessManager(object):
    def __init__(self, xml=None):
        """initialise the access manager, creates a root user with password root
        or loads from xml
        btw. logonKeys is NOT saved. This is deliberate (don't ask me why - it just seem to make sense)
        """
        # self.pwords is a dictionary from every username to its password
        self.pwords = {}
        # sets not lists, better
        self.root_group = set()
        # user tags:
        # users are tagged into classes etc.
        # this is a mapping from tags to sets of usernames
        # TODO: save and restore these
        self.tags = {}
        if xml:
            self.from_XML(xml)
        else:
            self.add_user('root','root')
            self.promote('root')
        self.logonKeys = {}
        
    def change_password(self, uname, pword):
        """change the password of an existing user
        returns nothing.
        raises InvalidLogin if the user doesn't exist
        Note: no password policies are enforced
        """
        if not self.test_user(uname):
            raise InvalidLogin()
        self.pwords[uname] = pword
    
    def test_user(self, uname):
        """tests if a given username exists"""
        return uname in self.pwords
    
    def do_login(self, uname, pword):
        """if the given login is correct, return a registered login key (a unique string)
        if the logon is invalid an InvalidLogon exception is raised
        """
        if not self.test_user(uname):
            raise InvalidLogin()
        elif self.pwords[uname] == pword:
            t = str(random())
            self.logonKeys[t] = AccessRecord((uname in self.root_group), uname)
            return t
        else:
            raise InvalidLogin()
        
    def promote(self, uname):
        """promote a user to root
        somebody should check that only root can do this
        """
        if (uname in self.pwords) and not (uname in self.root_group):
            self.root_group.add(uname)
    
    def to_XML(self):
        """return an XML tree representing this access system"""
        root_node = et.Element("access")
        pwords_node = et.SubElement(root_node, "pwords")
        for i in self.pwords.keys():
            t = et.SubElement(pwords_node, "pword", uname=i)
            t.text = self.pwords[i]
        rootgrp_node = et.SubElement(root_node, "root_group")
        for i in self.root_group:
            t = et.SubElement(rootgrp_node, "member")
            t.text = i
        return root_node
    
    def from_XML(self, root_node):
        """parse an XML tree"""
        for node in root_node.getchildren():
            if node.tag == 'pwords':
                for i in node.getchildren():
                    if i.tag == 'pword':
                        self.add_user(i.attrib['uname'], i.text)
            if node.tag == 'root_group':
                for i in node.getchildren():
                    if i.tag == 'member':
                        self.promote(i.text)
    
    def is_root(self, loginKey):
        """test if a given logonKey can do root stuff"""
        return self.logonKeys[loginKey].isRoot
    
    def can_access_user(self, loginKey, uname):
        return (self.logonKeys[loginKey].userName == uname) or self.is_root(loginKey)
    
    def add_user(self, uname, pword):
        """add a user"""
        if not self.test_user(uname):
            self.pwords[uname] = pword
        else:
            raise UnameInUse()
        
    def list_all_users(self):
        return self.pwords.keys()
    
    def is_root_user(self, uname):
        return uname in self.root_group
    
    def get_user_passwd(self, uname):
        if uname in self.pwords:
            return self.pwords[uname]
        else:
            return 0
    
    def tag_user(self, uname, tagname):
        """do the obvious, if a user already has the tag then don't complain"""
        if tagname not in self.tags:
            self.tags[tagname] = set()
        self.tags[tagname].add(uname)
    
    def untag_user(self, uname, tagname):
        """again, this should be obvious. If the user isn't tagged with the given tag, this doesn NOT complain"""
        if tagname in self.tags:
            if uname in self.tags[tagname]:
                self.tags[tagname].discard(uname)
    
    def get_tag_users(self, tagname):
        """get the users registered in a tag as a list"""
        ret = []
        for x in self.tags[tagname]:
            ret.add(x)
        return x
    
    def get_user_tags(self, uname):
        """get the tags that a user has as a list. 
        This has complexity Nusers * Ntags (must be a better way of doing this)"""
        ret = []
        for x in self.tags:
            for y in self.tags[x]:
                if y == uname:
                    ret.add(x)
                    break
        return ret
    
    def list_all_tags(self):
        return self.tags.keys()
    
class Student(object):
    """represents the record of an individual student"""
    def __init__(self, uname):
        self.log = []
        self.saved_data = {}
        self.submitted_data = {}
        if uname is types.StringType:
            self.uname = uname
        else:
            #assume its an XML tree
            self.from_XML(uname)
        
    def log(self, data):
        """log some data"""
        self.log.add(data)
        
    def save(self, key, data):
        """save some data to be retrieved later"""
        self.saved_data[key] = data
    
    def submitted_data(self, key, data):
        """submit some data for a teacher to inspect"""
        self.submitted_data[key] = data
        
    def to_XML(self):
        """return an XML tree which describes this Student's data"""
        root_node = et.Element("student", uname=uname)
        log_node = et.SubElement(root_node, "log")
        for i in self.log:
            n = et.SubElement(log_node, "log_element")
            n.text = i
        save_node = et.SubElement(root_node, "saved_data")
        for i in self.saved_data.keys():
            n = et.SubElement(save_node, "data", key=i)
            n.text = self.saved_data[i]
        submit_node = et.SubElement(root_node, "submitted_data")
        for i in self.submitted_data.keys():
            n = et.SubElement(submit_node, "data", key=i)
            n.text = self.submit_data[i]
        return root_node
    
    def from_XML(self, root_node):
        """parse XML"""
        self.uname = root_node.attrib['uname']
        for i in root_node.getchildren():
            if i.tag == "log":
                for j in i.getchildren():
                    if j.tag == "log_element":
                        self.log.append(j.text)
            elif i.tag == "saved_data":
                for j in i.getchildren():
                    if j.tag == "data":
                        self.saved_data[j.attrib['key']] = j.text
            elif i.tag == "submitted_data":
                for j in i.getchildren():
                    if j.tag == "data":
                        self.submitted_data[j.attrib['key']] = j.text
    
class ClassRoom(object):
    """represents a classroom, which is a collection of students"""
    def __init__(self):
        self.access = AccessManager()
        # mapping from unames (ie. strings) to Student objects:
        self.records = {}
    
    def change_password(self, login, uname, pword):
        """
        Change the password of a user.
        access is handled by the access manager
        returns 1 on success, 0 otherwise
        """
        if self.access.can_access_user(login, uname):
            self.access.change_password(uname, pword)
            return 1
        else:
            return 0
        
    def login(self, uname, pword):
        """do a login
        returns 0 if the login fails, a login key (as a string) otherwise
        the login key should then be used for calls to the other methods
        """
        try:
            t = self.access.do_login(uname, pword)
            return t
        except InvalidLogin:
            return 0
    
    def add_user_self(self, uname, pword):
        """Allows a user to add themselves without a login
        returns 1 on success, 0 otherwise
        """
        try:
            self.access.add_user(uname, pword)
            sef.__create_record(uname)
            return 1
        except UnameInUse:
            return 0
        
        
    def __create_record(self, login, uname):
        """create the record for a student if it doesn't exist yet"""
        if not (uname in self.records):
            self.records[uname] = Student(uname)
            
    def __to_XML(self):
        """return an XML elementtree representing the data"""
        root_node = et.Element('classroom_state')
        access_node = self.access.to_XML()
        root_node.append(access_node)
        records_node = et.SubElement(root_node, "records")
        for i in self.records.keys():
            records_node.append(self.records[i].to_XML())
        return root_node
    
    def __from_XML(self, root_node):
        """parse an XML tree"""
        access_node = root_node.findall('access')[0]
        self.access = AccessManager(access_node)
        self.records.clear()
        records_node = root_node.findall('records')[0]
        for i in records_node.getchildren():
            t = Student(i)
            self.records[t.uname] = t
            
    def to_XML_string(self):
        """produce an XML string representation of this ClassRoom, suitable for saving the complete state (backup)
        returns a string
        """
        return et.tostring(self.__to_XML)
    
    def list_all_users(self, login):
        """list every user in the system
        only root can do this
        return value is a list of strings
        or 0 if access was denied
        """
        if self.access.is_root(login):
            return self.access.list_all_users()
        else:
            return 0
        
    def is_root(self, login):
        """tests if the given login key is root
        returns 1 if it is, 0 else
        """
        if self.access.is_root(login):
            return 1
        return 0
    
    def is_root_user(self, login, uname):
        """tests if the given usename is root
        returns 1 if it is, 0 else
        this also always returns 0 if called with a non-root login key
        """
        if not self.access.is_root(login):
            return 0
        if self.access.is_root_user(uname):
            return 1
        return 0
        
    def promote(self, login, uname):
        """promote a user to admin
        returns 1 if successful, 0 otherwise
        """
        if not self.access.is_root(login):
            return 0
        else:
            self.access.promote(uname)
            return 1
        
    def get_user_passwd(self, login, uname):
        """get the password of a given user
        return the password or 0 if insufficient access
        0 is also returned if the user doesn't exist
        """
        if not self.access.can_access_user(login, uname):
            return 0
        else:
            return self.access.get_user_passwd(uname)
        
    def tag_user(self, login, uname, tagname):
        """tag a user.
        returns 1 on success, 0 else
        most probable failure is lack of access rights
        """
        if not self.access.can_access_user(login, uname):
            return 0
        else:
            self.access.tag_user(uname, tagname)
            return 1
    
    def untag_user(self, login, uname, tagname):
        """untag a user.
        returns 1 on success, 0 else
        most probable failure is lack of access rights
        """
        if not self.access.can_access_user(login, uname):
            return 0
        else:
            self.access.untag_user(uname, tagname)
            return 1
    
    def get_tag_users(self, login, tagname):
        """
        get a list of the users for a particular tag
        admin only
        returns a list of usernames on success, 0 else
        """
        if not self.access.is_root(login):
            return 0
        return self.access.get_tag_users(tagname)
    
    def get_user_tags(self, login, uname):
        """
        get a list of the tags for a particular user
        users can only access their own tag, admins can access them all
        returns a list of tagnames on success, 0 else
        """
        if not self.access.can_access_user(login, uname):
            return 0
        return self.access.get_user_tags(uname)
    
    def list_all_tags(self, login):
        """
        list every tag on the system
        any valid user can do this (although for now anybody can do it, login isn't checked)
        returns a list of tagnames
        """
        return self.access.list_all_tags()
    
    def log_action(self, login, uname, log_data):
        """
        log an action,
        returns 1 on success, 0 else
        """
        if not self.access.can_access_user(login, uname):
            return 0
        if uname not in self.records:
            self.__create_record(uname)
        self.records[uname].log(log)
        
    def get_log_list(self, login, uname):
        """
        get the log for a user,
        usual return codes: string list on success, string
        """
        if not self.access.can_access_user(login, uname):
            return 0
        return self.records[uname]
class AdminDocXMLRPCRequestHandler(DocXMLRPCRequestHandler):
    def do_GET(self):
        """override it to serve the admin pages"""
        print self.path
        if self.path == '/server-admin.html':
            data = open('server-admin.html').read()
        elif self.path == '/server-admin.js':
            data = open('server-admin.js').read()
        else:
            DocXMLRPCRequestHandler.do_GET(self)
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data)
        return
    def do_POST(self):
        """lets us listen in and log the requests neatly"""
        s = self.rfile.read(int(self.headers['Content-Length']))
        self.rfile = StringIO(s)
        #print s
        DocXMLRPCRequestHandler.do_POST(self)
    
if __name__ == '__main__':
    print "Crunchy Classroom server V0.0.1"
    server = DocXMLRPCServer(("localhost", 8000))
    # make it serve the admin pages:
    server.RequestHandlerClass = AdminDocXMLRPCRequestHandler
    server.register_introspection_functions()
    server.set_server_title("Crunchy Classroom Server")
    server.set_server_name("Crunchy Classroom Server")
    server.register_instance(ClassRoom())
    server.serve_forever()
