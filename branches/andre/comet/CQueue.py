"""
A Python Combinator Queue
If two subseququent items can be combined, they will be
"""

from time import sleep
from threading import RLock, Event

class Queueable(object):
    """abstract base class for all queueable objects"""
    def __init__(self, data, tag, channel):
        self.data = data
        self.tag = tag
        self.channel = channel
    def merge(self, next):
        """merge this queue element with the next one, returns true if successful"""
        return False
    def __repr__(self):
        return self.data
class QueueableMergeable(Queueable):
    """mergable text things to queue"""
    def merge(self, next):
        if (type(next) is QueueableMergeable) and (next.tag == self.tag) and (next.channel == self.channel):
            self.data += next.data
            return True
        else:
            return False


class CQueue(object):
    """implemented using python lists"""
    def __init__(self):
        self.data = []
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
                t = self.data[0]
                del self.data[0]
                self.lock.release()
                return t
            self.lock.release()
            self.get_event.wait()
            #sleep(0.5)

    def put(self, t):
        self.lock.acquire()
        if len(self.data) > 0:
            if not self.data[-1].merge(t):
                self.data.append(t)
        else:
            
            self.data.append(t)
        self.lock.release()
        self.get_event.set()
