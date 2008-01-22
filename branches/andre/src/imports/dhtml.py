'''dhtml.py

Enables dynamic display of images (from files) and other html tags/objects
on a page where no such object was preloaded.

This module is meant to be imported by a user at a Crunchy prompt or
inside an editor.
'''

# variable that start with "_" are not displayed in Crunchy's "help";
# we use this feature to only expose a small number of them to the user.
import os as _os
import src.interface as _interface
_plugin = _interface.plugin
_config = _interface.config

home = _os.path.expanduser("~")
temp_dir = _config['temp_dir']
join_path = _os.path.join

_nodes = {}
_roots = {}

class _Tree(object):
    '''simple tree structure to keep track of elements added and removed'''
    def __init__(self, label, parent=None):
        self.label = label
        self.parent = parent
        if parent is not None:
            parent.append_child(self)
        self.children = []
        self.deletedlabels = [] # for cleanup
        _nodes[label] = self
        
    def append_child(self, child):
        '''adds a child'''
        self.children.append(child)
    
    def remove_child(self, child):
        '''removes a single child and all of its children, grand-children, etc.'''
        child.delete()
        self.children.remove(child)
        del child
        
    def remove_all_children(self):
        '''removes all children, grand-children, etc., from a tree'''
        for child in self.children:
            child.delete()
        self.children = []
    
    def delete(self):
        '''deletes self and all children'''
        self.remove_all_children()
        for label in self.deletedlabels:
            self.parent.deletedlabels.append(label)
        self.parent.deletedlabels.append((self.label, self.parent.label))
        del _nodes[self.label]

def image(file_path, width=400, height=400, name='', from_cwd=False):
    ''' dynamically creates an html <img> tag displaying the resulting image.
    
    file_path can be either an absolute path on the local server,
    a fully qualified url (http://....) on a remote server,
    a relative path (or filename) from the Crunchy server root,
    or a relative path (or filename) from the current working directory
    if from_cwd is set to True.
    
    Different values for name allow to display more than one image; the
    last loaded image for a given name replaces the previous one.
    '''
    if from_cwd:
        file_path = _os.path.join(_os.getcwd(), file_path)
    append('img', attributes={'width':width, 'height':height, 'src':file_path},
           name=name)

def append(tag, attributes=None, name='', parentlabel=None):
    ''' dynamically creates an html object with the given attribute (as a dict).
    
    Different values for name allow to display more than one object; the
    last loaded object for a given name replaces the previous one.
    
    If parentlabel is None, the objects gets appended to the main <div> of
    the Python output element; otherwise, it gets appended to the specified
    parent
    '''
    uid = _plugin['get_uid']()
    child_uid = 'dhtml_' + uid + "_" + str(name)
    
    # identify the right parent
    if parentlabel is None and uid not in _roots:
        parent_tag = "div_"
        pid = parent_tag + uid
        _roots[uid] = _Tree(pid) # create the element
        parent = _roots[uid]
    elif parentlabel is None:
        parent_tag = "div_"
        pid = parent_tag + uid
        parent = _roots[uid]
    else:
        parent_tag = "dhtml_"
        pid = 'dhtml_' + uid + "_" + str(parentlabel)
        parent = _nodes[pid]
    
    # remove any existing child with the same id, and its own children
    if child_uid in _nodes:
        parent.remove_child(_nodes[child_uid]) # remove from tree
        for clabel, plabel in parent.deletedlabels: # remove from html page
            _js_remove_html(clabel, plabel)
        parent.deletedlabels = []
    
    # Create the new child
    _Tree(child_uid, parent)
    _js_append_html(pid, tag, child_uid, attributes)

def remove(name=''):
    ''' dynamically removes an html object that was previously created.
    '''
    uid = _plugin['get_uid']()
    child_uid = 'dhtml_' + uid + "_" + str(name)
    if child_uid not in _nodes:
        print("No object with this id was _created previously; name=" +
              str(name))
        return
    parent = _nodes[child_uid].parent
    parent.remove_child(_nodes[child_uid]) # remove from tree
    for clabel, plabel in parent.deletedlabels:
        _js_remove_html(clabel, plabel) # remove from page
    parent.deletedlabels = []

# The following functions send the required javascript code to the
# html page so as to dynamically append or remove elements.  They
# are not meant to be called directly by the user.

def _js_append_html(pid, tag, child_uid, attributes):
    '''appends an html element to a page'''
    _plugin['exec_js'](_plugin['get_pageid'](),
                      """var currentDiv = document.getElementById("%s");
                      var newTag = document.createElement("%s");
                      newTag.setAttribute('id', '%s');
                      currentDiv.appendChild(newTag);
                      """%(pid, tag, child_uid))
    if attributes is not None:
        tag_attr = []
        for key in attributes:
            tag_attr.append("document.getElementById('%s').%s='%s';"%(
                                    child_uid, key, attributes[key]))
        _plugin['exec_js'](_plugin['get_pageid'](), '\n'.join(tag_attr))

def _js_remove_html(child_uid, parent_uid):
    '''removes an html element from a page'''
    _plugin['exec_js'](_plugin['get_pageid'](),
                      """var currentDiv = document.getElementById("%s");
                      var obsolete = document.getElementById("%s");
                      currentDiv.removeChild(obsolete);
                      """%(parent_uid, child_uid))