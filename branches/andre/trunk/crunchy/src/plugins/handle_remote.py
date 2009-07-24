# -*- coding: utf-8 -*-
"""Handle remote loading of tutorials.

Defines the /remote http request path.
Creates a form allowing to specify the URL of a tutorial to be loaded
by Crunchy.
"""

import sys

# urllib reshuffled in Python 3.
if sys.version_info[0] < 3:
    from urllib import FancyURLopener, unquote_plus
else:
    from urllib.request import FancyURLopener
    from urllib.parse import unquote_plus

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, preprocessor, config, SubElement

provides = set(["/remote"])

def register():  # tested
    '''registers http handler for dealing with remote files as well as
    handler for inserting widget for loading remote tutorials.'''
    plugin['register_http_handler']("/remote", remote_loader)
    # 'load_remote' only appears inside <span> elements, using the notation
    # <span title='load_remote'>
    plugin['register_tag_handler']("span", "title", "load_remote",
                                                    insert_load_remote)
    plugin['add_vlam_option']('power_browser', 'remote_html')
    plugin['register_service']("remote_html", insert_load_remote)

def remote_loader(request):  # tested
    '''
    create a vlam page from a request to get a remote file
    '''
    url = unquote_plus(request.args["url"])
    extension = url.split('.')[-1]
    username = request.crunchy_username
    if extension in preprocessor:
        # TODO: preprocessor don't forward Accept-Language HTTP headers
        page = plugin['create_vlam_page'](
                    preprocessor[extension](url, local=False), url,
                                                username=username, remote=True)
    else:
        opener = FancyURLopener()
        if (config[username]["forward_accept_language"]
            and "Accept-Language" in request.headers):
            opener.addheader("Accept-Language", request.headers["Accept-Language"])
        page = plugin['create_vlam_page'](opener.open(url), url,
                                          username=username, remote=True)
    request.send_response(200)
    request.send_header('Cache-Control', 'no-cache, must-revalidate, no-store')
    request.end_headers()
    # write() in python 3.0 returns an int instead of None;
    # this interferes with unit tests
    dummy = request.wfile.write(page.read())

def insert_load_remote(dummy_page, parent, dummy_uid): # tested
    '''inserts a form to load a remote page'''
    # in general, page and uid are used by similar plugins, but they are
    # redundant here.
    form = SubElement(parent, 'form', name='url', size='80', method='get',
                       action='/remote')
    SubElement(form, 'input', name='url', size='80',
                           value=parent.text)
    input2 = SubElement(form, 'input', type='submit',
                           value='Load remote tutorial')
    input2.attrib['class'] = 'crunchy'
    parent.text = ' '
