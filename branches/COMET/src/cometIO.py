"""
does some asynch IO

"""

import threading
import interpreter
import sys
from CQueue import CQueue


# a set of active thread uids:
thread_set = set()
thread_lock = threading.RLock()

# a table of events indexed by the stream IDs
event_table = {}
event_lock = threading.RLock()

# a table of buffered input data indexed by stream IDs
input_table = {}
input_lock = threading.RLock()

# output queues indexed by pageid
output_queues = {}

def add_output_queue(pageid):
    output_queues[pageid] = CQueue()

def pack_output(css_class, uid, data):
    """pack some data in suitable javascript to display it on a page"""
    pdata = data.replace("\n", "\\n")
    pdata = pdata.replace('"', '&#34;')
    return """document.getElementById("out_%s").innerHTML += "<span class='%s'>%s</span>";""" % (uid, css_class, pdata)

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
    
def push_input(request):
    """for now assumes that the thread (uid) is redirected"""
    global event_lock, event_table, input_lock, input_table, output_queues
    uid = request.args["uid"]
    pageid = uid.split(":")[0]
    #push the data
    input_lock.acquire()
    input_table[uid] += request.data
    input_lock.release()
    output_queues[pageid].put(pack_output("stdin", uid, request.data))
    #fire the event:
    event_lock.acquire()
    event_table[uid].set()
    event_lock.release()
    request.send_response(200)
    request.end_headers()
    
def comet(request):
    """does output for a whole load of processes at once"""
    global output_queues
    pageid = request.args["pageid"]
    #wait for some data
    data = output_queues[pageid].get()
    # OK, data found
    request.send_response(200)
    request.end_headers()
    request.wfile.write(data)
    request.wfile.flush()
    

class ThreadedBuffer(object):
    """Split output acording to calling thread"""
    def __init__(self, out_buf=None, in_buf=None, buf_class="STDOUT"):
        """Initialise the object,
        out_buf is the default output stream, in_buf is input
        buf_class is a class to apply to the output - redirected output can be 
        put in an html <span /> element with class=buf_class.
        Interestingly, having two threads with the same uids shouldn't break anything :)
        """
        self.default_out = out_buf
        self.default_in = in_buf
        self.buf_class = buf_class
        
    def register_thread(self, uid):
        """register a thread for redirected IO, registers the current thread"""
        global output_queues, thread_lock, thread_set
        pageid = uid.split(":")[0]
        mythread = threading.currentThread()
        mythread.setName(uid)
        thread_lock.acquire()
        thread_set.add(uid)
        thread_lock.release()
        # clear the output:
        output_queues[pageid].put("""document.getElementById("in_%s").style.display="inline";""" % uid)
        
    def unregister_thread(self):
        """
        Uregister the current thread.
        This will cancel all pending input and cancel all ouput once it has been
        forwarded.
        Assumes that no more input will be written specifically for this thread.
        In future IO for this thread will go via the defaults.
        """
        global output_queues, input_lock, input_table, thread_lock, thread_set, event_lock, event_table
        uid = threading.currentThread().getName()
        if not self.__redirect(uid):
            return
        uid = threading.currentThread().getName()
        pageid = uid.split(":")[0]
        input_lock.acquire()
        del input_table[uid]
        input_lock.release()
        thread_lock.acquire()
        thread_set.discard(uid)
        thread_lock.release()
        event_lock.acquire()
        event_table[uid].set()
        event_lock.release()
        output_queues[pageid].put(reset_js % (uid, uid, uid))
        
    def write(self, data):
        """write some data"""
        global output_queues
        uid = threading.currentThread().getName()
        pageid = uid.split(":")[0]
        if self.__redirect(uid):
            output_queues[pageid].put(pack_output(self.buf_class, uid, data))
        else:
            self.default_out.write(data)
        
    def read(self, length=0):
        """len is ignored, N.B. this function is rarely, if ever, used - and is probably untested"""
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
sys.stdout = ThreadedBuffer(out_buf=sys.stdout, buf_class="stdout")
sys.stderr = ThreadedBuffer(out_buf=sys.stderr, buf_class="stderr")

reset_js = """
document.getElementById("in_%s").style.display="inline";
document.getElementById("out_%s").innerHTML="";
document.getElementById("canvas_%s").style.display="none";
"""
