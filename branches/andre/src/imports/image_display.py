'''image_display.py

Enables dynamic display of images (from files) on a page where no image was
preloaded.
'''
# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin

created_uids = []

def show(file_path, width=400, height=400):
    uid = plugin['get_uid']()
    if uid not in created_uids: # dynamically create an image
        created_uids.append(uid)
        plugin['exec_js'](plugin['get_pageid'](), """var divImage = document.getElementById("div_%s");
                        var newImage = document.createElement("img");
                        newImage.setAttribute('id', 'img_%s');
                        divImage.appendChild(newImage);
        """%(uid, uid))
        print "new image created; uid = ", uid
    plugin['exec_js'](plugin['get_pageid'](), """document.getElementById("img_%s").width=%d;
                    document.getElementById("img_%s").height=%d;
                    document.getElementById("img_%s").src='%s';
                    """ % (uid, width, uid, height, uid, file_path))

