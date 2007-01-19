"""
do some asynch IO
queue_data() is used to queue up input
"""

import threading
import interpreter
import sys

uids = 0

comet_header = """
<html>
<head>
<title>crunchy comet</title>
</head>
<body>
<pre id="out">
test
</pre>
</body>
</html>
"""
comet_separator = """
</script><script>
"""

# a set of active thread uids:
thread_set = set()
thread_lock = threading.RLock()

# a table of events indexed by the stream IDs, event table entries are tuples of
#  (input_event, output_event)
event_table = {}
event_lock = threading.RLock()

# a table of buffered input data indexed by stream IDs
input_table = {}
input_lock = threading.RLock()

# a table of buffered output data indexed by stream IDs
output_table = {}
output_lock = threading.RLock()

def do_exec(code):
    """exec code in a new thread (and isolated environment), returning a 
    unique IO stream identifier"""
    global uids, output_table, event_table, output_lock, event_lock, input_lock, input_table
    uid = str(uids)
    uids += 1
    t = interpreter.Interpreter(code, uid)
    t.setDaemon(True)
    #set up all the tables:
    output_lock.acquire()
    output_table[uid]=""
    output_lock.release()
    input_lock.acquire()
    input_table[uid]=""
    input_lock.release()
    event_lock.acquire()
    event_table[uid]=threading.Event()
    event_lock.release()
    t.start()
    return uid
            
def push_input(request):
    """for now assumes that the thread (uid) is redirected"""
    global event_lock, event_table, input_lock, input_table, output_lock, output_table
    uid = request.args["uid"]
    #push the data
    input_lock.acquire()
    input_table[uid] += request.data
    input_lock.release()
    output_lock.acquire()
    output_table[uid] += (request.data)
    output_lock.release()
    #fire the event:
    event_lock.acquire()
    event_table[uid].set()
    event_lock.release()
    
def comet(request):
    """does output"""
    global event_lock, event_table, output_lock, output_table, thread_lock, thread_set
    uid = request.args["uid"]
    #get the event
    event_lock.acquire()
    event = event_table[uid]
    event_lock.release()
    #wait for some data
    while True:
        event.clear()
        output_lock.acquire()
        if output_table[uid]:
            data = output_table[uid]
            output_table[uid] = ""
            output_lock.release()
            break
        output_lock.release()
        # if we get here then there is currently no output to be written
        # check if there ever will be:
        thread_lock.acquire()
        if uid not in thread_set:
            request.send_response(400) #no good, give up - there never will be any more data
            request.end_headers()
            thread_lock.release()
            return
        thread_lock.release()
        event.wait()
    # OK, data found and valid
    request.send_response(200)
    request.end_headers()
    request.wfile.write(data)
    request.wfile.flush()
    
        
class ThreadedBuffer(object):
    """Split output acording to calling thread"""
    def __init__(self, out_buf=None, in_buf=None, buf_class=None):
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
        global thread_lock, thread_set
        mythread = threading.currentThread()
        mythread.setName(uid)
        thread_lock.acquire()
        thread_set.add(uid)
        thread_lock.release()
        
    def unregister_thread(self):
        """
        Uregister the current thread.
        This will cancel all pending input and cancel all ouput once it has been
        forwarded.
        Assumes that no more input will be written specifically for this thread.
        In future IO for this thread will go via the defaults.
        """
        global input_lock, input_table, thread_lock, thread_set, event_lock, event_table
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
        
    def write(self, data):
        """write some data"""
        global output_table, event_table, output_lock, event_lock
        uid = threading.currentThread().getName()
        if self.__redirect(uid):
            # transform the data:
            if self.buf_class:
                data = '<span class="%s">%s</span>' % (self.buf_class, data)
            #queue up the data:
            output_lock.acquire()
            output_table[uid] += data
            output_lock.release()
            #and fire off the notification event
            event_lock.acquire()
            event_table[uid].set()
            event_lock.release()
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
sys.stdout = ThreadedBuffer(out_buf=sys.stdout, buf_class="stdout")
sys.stderr = ThreadedBuffer(out_buf=sys.stderr, buf_class="stderr")
