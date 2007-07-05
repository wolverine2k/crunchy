"""
Handles all the Output - ie. is used to push javascript code
to the page asynchronously.
Also handles the redirection of stdin, stdout and stderr.
"""

import threading
import interpreter
import sys

import configuration

debug_enabled = False

class StringBuffer(object):
    """A thread safe buffer used to queue up strings that can be appended
    together, I've left this in a separate class because it might one day be
    useful someplace else"""
    def __init__(self):
        self.lock = threading.RLock()
        self.event = threading.Event()
        self.data = ""
    def get(self):
        """get the current contents of the buffer, if the buffer is empty, this
        always blocks until data is available.
        Multiple clients are handled in no particular order"""
        debug_msg("entering StringBuffer.get")
        while True:
            self.event.clear()
            self.lock.acquire()
            if len(self.data) > 0:
                t = self.data
                self.data = ""
                self.lock.release()
                debug_msg("leaving StringBuffer.get: " + t)
                return t
            self.lock.release()
            self.event.wait()
    def getline(self):
        """basically does the job of readline"""
        debug_msg("entering StringBuffer.get")
        while True:
                self.event.clear()
                self.lock.acquire()
                data_t = self.data.split("\n", 1)
                if len(data_t) > 1:
                    # we have a complete line, do something with it
                    self.data = data_t[1]
                    self.lock.release()
                    debug_msg("leaving StringBuffer.getline: " + data_t[0])
                    return data_t[0] + "\n"
                # no luck:
                self.lock.release()
                self.event.wait()
    def put(self, data):
        """put some data into the buffer"""
        debug_msg("entering StringBuffer.put: " + data)
        self.lock.acquire()
        self.data += data
        self.event.set()
        self.lock.release()


class CrunchyIOBuffer(StringBuffer):
    """A version optimised for crunchy IO"""
    def put_output(self, data, uid):
        """put some output into the pipe"""
        data = data.replace('"', '&#34;')
        pdata = data.replace("\n", "\\n")
        pdata = pdata.replace("\r", "\\r")
        self.lock.acquire()
        if self.data.endswith('";//output\n'):
            self.data = self.data[:-11] + '%s";//output\n' % (pdata)
            self.event.set()
        else:
            self.put("""document.getElementById("out_%s").innerHTML += "%s";//output\n""" % (uid, pdata))
        self.lock.release()

# there is one CrunchyIOBuffer for output per page:
output_buffers = {}
# and one StringBuffer per input widget:
input_buffers = {}

def comet(request):
    """An http path handler, called from the page - blocks until there is data
    to be sent.
    This needs to be registered as a handler when Crunchy is launched."""
    pageid = request.args["pageid"]
    #wait for some data
    data = output_buffers[pageid].get()
    # OK, data found
    request.send_response(200)
    request.end_headers()
    request.wfile.write(data)
    request.wfile.flush()

def register_new_page(pageid):
    """Sets up the output queue for a new page"""
    output_buffers[pageid] = CrunchyIOBuffer()

def write_js(pageid, jscode):
    """write some javascript to a page"""
    output_buffers[pageid].put(jscode)

def write_output(pageid, uid, output):
    output_buffers[pageid].put_output(output, uid)

def do_exec(code, uid):
    """exec code in a new thread (and isolated environment).
    """
    # configuration.defaults._prefix = '_crunchy_' is the
    # instance name that can be used to get/set the various
    # configuration variables from within a user-written program.
    symbols = { configuration.defaults._prefix : configuration.defaults}
    t = interpreter.Interpreter(code, uid, symbols=symbols)
    t.setDaemon(True)
    t.start()

def push_input(request):
    """An http request handler to deal with stdin"""
    uid = request.args["uid"]
    pageid = uid.split(":")[0]
    # echo back to output:
    output_buffers[pageid].put_output("<span class='stdin'>" + request.data + "</span>", uid)
    input_buffers[uid].put(request.data)
    request.send_response(200)
    request.end_headers()

class ThreadedBuffer(object):
    """Split some IO acording to calling thread"""
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
        pageid = uid.split(":")[0]
        mythread = threading.currentThread()
        mythread.setName(uid)
        input_buffers[uid] = StringBuffer()
        # display the input box and reset the output:
        #output_buffers[pageid].put(reset_js % (uid, uid, uid))
        output_buffers[pageid].put(reset_js % (uid, uid))#, uid))

    def unregister_thread(self):
        """
        Uregister the current thread.
        This will cancel all pending input
        Assumes that no more input will be written specifically for this thread.
        In future IO for this thread will go via the defaults.
        """
        uid = threading.currentThread().getName()
        if not self.__redirect(uid):
            return
        pageid = uid.split(":")[0]
        del input_buffers[uid]
        # hide the input box:
        output_buffers[pageid].put("""document.getElementById("in_%s").style.display="none";""" % uid)


    def write(self, data):
        """write some data"""
        uid = threading.currentThread().getName()
        pageid = uid.split(":")[0]
        if self.__redirect(uid):
            output_buffers[pageid].put_output(("<span class='%s'>" % self.buf_class) + data + '</span>', uid)
        else:
            self.default_out.write(data)

    def read(self, length=0):
        """len is ignored, N.B. this function is rarely, if ever, used - and is probably untested"""
        uid = threading.currentThread().getName()
        if self.__redirect(uid):
            #read the data
            data = input_buffers[uid].get()
        else:
            data = self.default_in.read()
        return data

    def readline(self, length=0):
        """len is ignored, can block, complex and oft-used, needs a testcase"""
        uid = threading.currentThread().getName()
        if self.__redirect(uid):
            data = input_buffers[uid].getline()
        else:
            data = self.default_in.readline()
        return data

    def __redirect(self, uid):
        """decide if the thread with uid uid should be redirected"""
        t = uid in input_buffers
        return t

    def default_write(self, data):
        """write to the default output"""
        self.default_out.write(data)

def debug_msg(data):
    """write a debug message, debug messages always appear on stderr"""
    if debug_enabled:
        sys.stderr.default_write(data + "\n")

sys.stdin = ThreadedBuffer(in_buf=sys.stdin)
sys.stdout = ThreadedBuffer(out_buf=sys.stdout, buf_class="stdout")
sys.stderr = ThreadedBuffer(out_buf=sys.stderr, buf_class="stderr")

reset_js = """
document.getElementById("in_%s").style.display="inline";
document.getElementById("out_%s").innerHTML="";
"""
#
"""
document.getElementById("canvas_%s").style.display="none";
"""
