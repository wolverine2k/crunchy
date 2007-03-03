"""
do some asynch IO
queue_data() is used to queue up input
"""

import threading
import interpreter
import sys
from CQueue import CQueue, Queueable, QueueableMergeable

QBL = Queueable
QBLM = QueueableMergeable



# a set of active thread uids:
thread_set = set()
thread_lock = threading.RLock()

# a table of events indexed by the stream IDs
event_table = {}
event_lock = threading.RLock()

# a table of buffered input data indexed by stream IDs
input_table = {}
input_lock = threading.RLock()

# an output queue of pairs of (type, channel, data)
# type is on of "STDOUT", "STDERR", "STDIN", "STOP", "RESET"
output_queue = CQueue()

def do_exec(code, uid):
    """exec code in a new thread (and isolated environment), returning a 
    unique IO stream identifier"""
    global event_table, output_lock, event_lock, input_lock, input_table
    t = interpreter.Interpreter(code, uid)
    t.setDaemon(True)
    #set up all the tables:
    input_lock.acquire()
    input_table[uid]=""
    input_lock.release()
    event_lock.acquire()
    event_table[uid]=threading.Event()
    event_lock.release()
    t.start()

def exec_callback(request):
    do_exec(request.data, request.args["uid"])
    
def push_input(request):
    """for now assumes that the thread (uid) is redirected"""
    global event_lock, event_table, input_lock, input_table, output_queue
    uid = request.args["uid"]
    #push the data
    input_lock.acquire()
    input_table[uid] += request.data
    input_lock.release()
    output_queue.put(QBLM(request.data, "STDIN", uid))
    #fire the event:
    event_lock.acquire()
    event_table[uid].set()
    event_lock.release()
    request.send_response(200)
    request.end_headers()
    
def comet(request):
    """does output for a whole load of processes at once"""
    global output_queue
    #wait for some data
    data = output_queue.get()
    # OK, data found
    request.send_response(200)
    request.end_headers()
    request.wfile.write(data.tag+" "+data.channel+"\n")
    request.wfile.write(data.data)
    request.wfile.flush()
    

class ThreadedBuffer(object):
    """Split output acording to calling thread"""
    def __init__(self, out_buf=None, in_buf=None, buf_class="STDOUT"):
        """Initialise the object,
        out_buf is the default output stream, in_buf is input
        buf_class is a class to apply to the output - redirected output can be 
        put in an html <span /> elemnt with class=buf_class.
        Interestingly, having two threads with the same uids shouldn't break anything :)
        """
        self.default_out = out_buf
        self.default_in = in_buf
        self.buf_class = buf_class
        
    def register_thread(self, uid):
        """register a thread for redirected IO, registers the current thread"""
        global output_queue, thread_lock, thread_set
        mythread = threading.currentThread()
        mythread.setName(uid)
        thread_lock.acquire()
        thread_set.add(uid)
        thread_lock.release()
        output_queue.put(QBL("","RESET", uid))
        
    def unregister_thread(self):
        """
        Uregister the current thread.
        This will cancel all pending input and cancel all ouput once it has been
        forwarded.
        Assumes that no more input will be written specifically for this thread.
        In future IO for this thread will go via the defaults.
        """
        global output_queue, input_lock, input_table, thread_lock, thread_set, event_lock, event_table
        uid = threading.currentThread().getName()
        if not self.__redirect(uid):
            return
        uid = threading.currentThread().getName()
        input_lock.acquire()
        del input_table[uid]
        input_lock.release()
        thread_lock.acquire()
        thread_set.discard(uid)
        thread_lock.release()
        event_lock.acquire()
        event_table[uid].set()
        event_lock.release()
        output_queue.put(QBL("","STOP", uid))
        
    def write(self, data):
        """write some data"""
        global output_queue
        uid = threading.currentThread().getName()
        if self.__redirect(uid):
            output_queue.put(QBLM(data, self.buf_class, uid))
        else:
            self.default_out.write(data)
        
    def read(self, length=0):
        """len is ignored, N.B. this function is rarely, if ever, used - and is untested"""
        global input_lock, input_table
        uid = threading.currentThread().getName()
        if self.__redirect(uid): 
            input_lock.acquire()
            #read the data
            data = input_table[uid]
            #reset the buffer
            input_table[uid] = ""
            input_lock.release()
        else:
            data = self.default_in.read()
        return data
        
    def readline(self, length=0):
        """len is ignored, can block, complex and oft-used, needs a doctest"""
        global input_lock, input_table, event_table, event_lock
        uid = threading.currentThread().getName()
        if self.__redirect(uid): 
            #get the event:
            event_lock.acquire()
            event = event_table[uid]
            event_lock.release()
            while True:
                event.clear()
                input_lock.acquire()
                data_t = input_table[uid].split("\n", 1)
                if len(data_t) > 1:
                    # we have a complete line, do something with it
                    input_table[uid] = data_t[1]
                    input_lock.release()
                    data = data_t[0] + "\n"
                    break
                # no luck:
                input_lock.release()
                event.wait()
        else:
            data = self.default_in.readline()
        return data
        
    def __redirect(self, uid):
        """decide if the thread with uid uid should be redirected"""
        global thread_lock, thread_set
        thread_lock.acquire()
        t = uid in thread_set
        thread_lock.release()
        return t
        
sys.stdin = ThreadedBuffer(in_buf=sys.stdin)
sys.stdout = ThreadedBuffer(out_buf=sys.stdout, buf_class="STDOUT")
sys.stderr = ThreadedBuffer(out_buf=sys.stderr, buf_class="STDERR")
