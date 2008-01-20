'''dhtml.py

Enables dynamic display of images (from files) and other html tags/objects
on a page where no such object was preloaded.
'''
import os
# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, config

home = os.path.expanduser("~")
temp_dir = config['temp_dir']

_created_uids = []

def image(file_path, width=200, height=200, local_id='', from_cwd=False):
    ''' dynamically creates an html <img> tag displaying the resulting image.
    
    file_path can be either an absolute path on the local server,
    a fully qualified url (http://....) on a remote server,
    a relative path (or filename) from the Crunchy server root,
    or a relative path (or filename) from the current working directory
    if from_cwd is set to True.
    
    Different values for local_id allow to display more than one image; the
    last loaded image for a given local_id replaces previous ones.
    '''
    uid = plugin['get_uid']()
    img_uid = uid + str(local_id)
    if from_cwd:
        file_path = os.path.join(os.getcwd(), file_path)
    
    append('img', attributes={'width':width, 'height':height, 'src':file_path},
           local_id=local_id)

def append(tag, attributes=None, local_id=''):
    ''' dynamically creates an html object with the given attribute (as a dict).
    
    Different values for local_id allow to display more than one object; the
    last loaded object for a given local_id replaces previous ones.
    '''
    uid = plugin['get_uid']()
    tag_uid = uid + str(local_id)
    if tag_uid not in _created_uids:
        _created_uids.append(tag_uid)
        plugin['exec_js'](plugin['get_pageid'](),
                          """var currentDiv = document.getElementById("div_%s");
                          var newTag = document.createElement("%s");
                          newTag.setAttribute('id', 'dhtml_%s');
                          currentDiv.appendChild(newTag);
                          """%(uid, tag, tag_uid))
    if attributes is not None:
        tag_attr = []
        for key in attributes:
            tag_attr.append("document.getElementById('dhtml_%s').%s='%s';"%(
                                    tag_uid, key, attributes[key]))
    plugin['exec_js'](plugin['get_pageid'](), '\n'.join(tag_attr))
    
def remove(local_id=''):
    ''' dynamically removes an html object that was previously created.
    '''
    uid = plugin['get_uid']()
    tag_uid = uid + str(local_id)
    if tag_uid not in _created_uids:
        print("No object with this id was _created previously; local_id=" +
              str(local_id))
    else:
        _created_uids.remove(tag_uid)
        plugin['exec_js'](plugin['get_pageid'](),
                          """var currentDiv = document.getElementById("div_%s");
                          var obsolete = document.getElementById("dhtml_%s");
                          currentDiv.removeChild(obsolete);
                          """%(uid, tag_uid))