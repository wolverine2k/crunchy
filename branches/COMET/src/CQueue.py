"""
A Thread safe Python Buffer
"""

from time import sleep
from threading import RLock, Event

class CQueue(object):
    """implemented using python lists"""
    def __init__(self):
        self.data = ""
        self.lock = RLock()
        self.get_event = Event()
    def size(self):
        """only approximately right"""
        return len(self.data)
        
    def get(self):
        """always blocks until new data available, multiple clients will 
        be handled in a non-det order"""
        while True:
            self.get_event.clear()
            self.lock.acquire()
            if len(self.data) > 0:
                t = self.data
                self.data = ""
                self.lock.release()
                return t
            self.lock.release()
            self.get_event.wait()
            #sleep(0.5)

    def put(self, t):
        self.lock.acquire()
        self.data += ("\n"+t)
        self.lock.release()
        self.get_event.set()
