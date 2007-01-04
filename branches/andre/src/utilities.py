'''utilities.py

Contain various function and classes for general use.

fixLineEnding: converts all line endings to '\n'
ThreadStream: class used to redirect stdout and stderr.
'''

import re
import threading


def fixLineEnding(txt):
    # Python recognize line endings as '\n' whereas, afaik:
    # Windows uses '\r\n' to identify line endings
    # *nix uses '\n'   (ok :-)
    # Mac OS uses '\r'
    # So, we're going to convert all to '\n'
    txt1 = re.sub('\r\n', '\n', txt) # Windows: tested
    txt = re.sub('\r', '\n', txt1)  # not tested yet: no Mac :-(
    return txt


class ThreadStream(object):
    """ Split output acording to calling thread """
    
    def __init__(self, default_out):
        """Initialise the object,
        default_out is the default output stream.
        If a thread has been registered, its data is buffered, else its data 
        is passed to default_out.
        Buffered data can be accessed by id
        """
        self.default_out = default_out
        #map id's to buffer's
        self.buffers = {}
        self.lock = threading.RLock()
        
    def register_thread(self, id = "default"):
        self.lock.acquire()
        mythread = threading.currentThread()
        mythread.setName(id)
        self.buffers[id] = ""
        self.lock.release()
        
    def write(self, data):
        self.lock.acquire()
        id = threading.currentThread().getName()
        if id in self.buffers:
            self.buffers[id] += data
        else:
            self.default_out.write(data)
        self.lock.release()
        
    def get_by_id(self, id):
        self.lock.acquire()
        data = ""
        if id in self.buffers:
            data = self.buffers[id]
            self.buffers[id] = ""
        self.lock.release()
        return data
