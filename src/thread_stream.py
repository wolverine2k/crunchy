"""
Split output acording to calling thread
"""

import threading

class ThreadStream(object):
    def __init__(self, default_out):
        """Initialise the object,
        default_out is the default output stream.
        If a thread has been registered, it's data is buffered, else it's data 
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
        #sys.__stderr__.write(repr(mythread))
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
