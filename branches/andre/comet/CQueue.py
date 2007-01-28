"""
A Python Combinator Queue
If two subseququent items can be combined, they will be
"""

from time import sleep
from threading import RLock, Event

class SingleOutput(object):
    """Mergeable Queues"""
    def __init__(self, data, tag, channel):
        self.data = data
        self.tag = tag
        self.channel = channel

    def can_merge(self, other):
        if other.data and (other.tag == self.tag) and (other.channel == self.channel):
            return True
        else:
            return False


class OutputQueue(object):
    """implemented using python lists"""
    def __init__(self):
        self.queues = []
        self.lock = RLock()
        self.event = Event()

    def get(self):
        """always blocks until new data available, multiple clients will
        be handled in a non-det order"""
        while True:
            self.event.clear()
            self.lock.acquire()
            if len(self.queues) > 0:
                t = self.queues[0]
                del self.queues[0]
                self.lock.release()
                return t
            self.lock.release()
            self.event.wait()

    def put(self, output):
        self.lock.acquire()
        if len(self.queues) > 0:
            if self.queues[-1].can_merge(output):
                self.queues[-1].data += output.data
            else:
                self.queues.append(output)
        else:
            self.queues.append(output)
        self.lock.release()
        self.event.set()
