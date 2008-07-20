""" Crunchy Input/Output Hook Plugin 
Do something when the input/output  happpens
"""
# All plugins should import the crunchy plugin API

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin
import re

# The set of other "widgets/services" required from other plugins
requires =  set()

provides = set(["register_io_hook", "apply_io_hook"])

def register():
    '''register a service'''
    plugin['register_service']("register_io_hook", register_io_hook)
    #plugin['register_service']("unregister_io_hook", unregister_io_hook)
    plugin['register_service']("apply_io_hook", apply_io_hook)

hook_names =(
    'before_input',
    'after_input',
    'before_output',
    'after_output'
)

_io_hooks = {}

def register_io_hook(hook, func, uid = 'ANY'):
    assert hook in hook_names
    if uid not in _io_hooks:
        _io_hooks[uid] = {}
        for hook_name in hook_names:
            _io_hooks[uid][hook_name] = []
    _io_hooks[uid][hook].append(func)
    
def apply_io_hook(uid, hook, data):
    if uid not in _io_hooks:
        return data
    elif hook not in _io_hooks[uid]:
        return data
    else:
        for func in _io_hooks[uid][hook]:
            data = func(data, uid)
        return data

