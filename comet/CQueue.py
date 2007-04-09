"""
CQueue.py

A Python queue is created to accumulate execution outputs until they are
ready to be called.
If two subseququent items can be combined, they will be.
"""

from time import sleep
from threading import RLock, Event

class SingleOutput(object):
    """
    Class holding (partial) output result from executing a script.

    The output can be directed either to the (redirected) standard output
    or standard error stream.  Each script is executed in a separate
    environment, to which a "channel id" is assigned.  So, a given
    output is characterised by 3 quantities: the actual data, the channel id
    and the response type.
    The various response types are:
    * STDOUT: data is raw (standard) output to be appended to the output
              of the IO elemnt denoted by Channel-Id.
    * STDERR: Is similar, but for stderr output.
    * STOP: Indicates that ouput has ended, tells the client to disable
            input for that element.
    * RESET: tells the client to reset the given IO Element.
    * JSCODE: Will execute the given Javascript code within the page.
              Currently not implemented.
    * POPUP: Will display a popup (possibly just using alert()) to give status
    information to the user. Currently not implemented.
    """
    def __init__(self, data, tag, channel):
        self.data = data
        self.tag = tag
        self.channel = channel

    def can_merge(self, other):
        """Determine if a given output can be joined/appended to an other one
           into a single stream in the queue.
        """
        if other.data and (other.tag == self.tag) and (other.channel == self.channel):
            return True
        else:
            return False


class OutputQueue(object):
    """All the single outputs (see class SingleOutput for details) are
       queued up until they are sent to the html page and update the display.
    """
    def __init__(self):
        self.queues = []
        self.lock = RLock()
        self.event = Event()

    def get(self):
        """return any available output from the queue and purges it.
           Always blocks until new data available; multiple clients will
           be handled in an indeterminate order.
        """
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
        """add a given output (obtained as a SingleOutput instance)
           to the output queue, merging the data with a previous
           output if possible.
           This could be generalised so that it checks if an output can be
           merged with any other previous outputs, rather than the immediately
           previous one.
        """
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
