"""
Handles all the Output - ie. is used to push javascript code
to the page asynchronously.
Also handles the redirection of stdin, stdout and stderr.
"""

import threading
import sys

import src.interpreter as interpreter
import src.utilities as utilities
import src.interface as interface

from src.interface import config, accounts, names

debug_ids = [1, 2, 3, 4, 5, 6]

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
        debug_msg("entering StringBuffer.get", 1)
        while True:
            debug_msg("begin loop", 5)
            self.event.clear()
            debug_msg("cleared events", 5)
            self.lock.acquire()
            debug_msg("acquired lock", 5)
            if len(self.data) > 0:
                t = self.data
                self.data = ""
                self.lock.release()
                debug_msg("leaving StringBuffer.get: " + t, 1)
                return t
            self.lock.release()
            debug_msg("released lock", 5)
            self.event.wait()

    def getline(self, uid):
        """basically does the job of readline"""
        debug_msg("entering StringBuffer.getline", 2)
        while True:
            self.event.clear()
            self.lock.acquire()
            data_t = self.data.split("\n", 1)
            if len(data_t) > 1:
                # we have a complete line, do something with it
                self.data = data_t[1]
                self.lock.release()
                debug_msg("leaving StringBuffer.getline: " + data_t[0] +
                                                        "end_of_data", 2)
                return uid, data_t[0] + "\n"
            # no luck:
            self.lock.release()
            self.event.wait()

    def put(self, data):
        """put some data into the buffer"""
        debug_msg("entering StringBuffer.put: " + data, 3)
        self.lock.acquire()
        self.data += data
        self.event.set()
        self.lock.release()


class CrunchyIOBuffer(StringBuffer):
    """A version optimised for crunchy IO"""
    help_flag = False

    def put_output(self, data, uid):
        """put some output into the pipe"""
        data = data.replace('"', '&#34;')
        pdata = data.replace("\n", "\\n")
        pdata = pdata.replace("\r", "\\r")
        debug_msg("pdata = "+ pdata, 4)
        self.lock.acquire()
        pageid = uid.split(":")[0]
        username = names[pageid]
        debug_msg("username = %s in CrunchyIOBuffer.put_output"%username, 5)
        if self.data.endswith('";//output\n'):
            self.data = self.data[:-11] + '%s";//output\n' % (pdata)
            # Saving session; appending from below
            if uid in config[username]['logging_uids']:
                log_id = config[username]['logging_uids'][uid][0]
                config[username]['log'][log_id].append(data)
                utilities.log_session()
            self.event.set()
        elif self.help_flag == True:
            self.put(help_js)
            pdata = pdata.replace("stdout", "help_menu") # replacing css class
            self.put("""document.getElementById("help_menu").innerHTML = "%s";\n""" % (pdata))
            self.help_flag = False
        else:
            self.put("""document.getElementById("out_%s").innerHTML += "%s";//output\n""" % (uid, pdata))
            # Saving session; first line...
            if uid in config[username]['logging_uids']:
                log_id = config[username]['logging_uids'][uid][0]
                config[username]['log'][log_id].append(data)
                utilities.log_session()
        self.lock.release()

# there is one CrunchyIOBuffer for output per page:
output_buffers = {}
# and one StringBuffer per input widget:
input_buffers = {}
# and also one thread per input widget:
threads = {}

def kill_thread(uid):
    """Kill a thread, given an associated uid"""
    threads[uid].terminate()

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
interface.from_comet['register_new_page'] = register_new_page

def write_js(pageid, jscode):
    """write some javascript to a page"""
    output_buffers[pageid].put(jscode)

def write_output(pageid, uid, output):
    '''write some simple output to an element identified by its uid'''
    try:
        output_buffers[pageid].put_output(output, uid)
    except:
        debug_msg("Problem in write_output", 6)

def do_exec(code, uid, doctest=False):
    """exec code in a new thread (and isolated environment).
    """
    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    try:
        pageid = uid.split(":")[0]
        username = names[pageid]
    except:
        debug_msg("error in do_exec; uid =%s"%uid, 5)
        return

    if 'display' in config[username]['get_current_page_security_level']():
        return
    elif not accounts:  # same if no username/password set
        return

    debug_msg(" creating an intrepreter instance in cometIO.do_exec()", 5)
    t = interpreter.Interpreter(code, uid, symbols=config[username]['symbols'],
                                doctest=doctest)

    debug_msg(" setting a daemon thread in cometIO.do_exec()", 5)
    t.setDaemon(True)
    debug_msg("  starting the thread in cometIO.do_exec()", 5)
    t.start()
    debug_msg("reached the end of cometIO.do_exec()", 5)

def push_input(request):
    """An http request handler to deal with stdin"""
    uid = request.args["uid"]
    pageid = uid.split(":")[0]
    # echo back to output:
    in_to_browser = utilities.changeHTMLspecialCharacters(request.data)
    output_buffers[pageid].put_output("<span class='stdin'>" +
                                            in_to_browser + "</span>", uid)
    # display help menu on a seperate div
    if request.data.startswith("help("):
        output_buffers[pageid].help_flag = True

    # ipython style help
    if request.data.rstrip().endswith("?"):
        output_buffers[pageid].help_flag = True
        help_str = "help(" + request.data.rstrip()[:-1] + ")\n"
        input_buffers[uid].put(help_str)
    else:
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
# Unfortunately, IPython interferes with Crunchy.
# The following is kept un-commented (unlike the rest of the IPython stuff
# which has been commented out) so that users can try the relevant
# code to start IPython from an interpreter or an editor and see
# what happens.
    # the encoding is required by IPython but currently ignored by Crunchy.
        self.encoding = 'utf-8'
    # the following is defined as a dummy function to make IPython work;
    # it is currently ignored by Crunchy.
    def flush(self):
        '''
        dummy function required by IPython; otherwised ignored by Crunchy.

        Currently unused.
        '''
        return
#====     end of IPython stuff

    def register_thread(self, uid):
        """register a thread for redirected IO, registers the current thread"""
        pageid = uid.split(":")[0]
        mythread = threading.currentThread()
        mythread.setName(uid)
        input_buffers[uid] = StringBuffer()
        threads[uid] = threading.currentThread()
        output_buffers[pageid].put(reset_js % (uid, uid, uid))

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
        output_buffers[pageid].put("""
            document.getElementById("in_%s").style.display="none";
            document.getElementById("kill_%s").style.display="none";
            """ % (uid,uid))


    def write(self, data):
        """write some data"""
        #
        # Note: even though we create interpreters in separate threads
        # identified by their uid, Borg interpreters share a common
        # state.  As a result, if we have long running code in one
        # Borg interpreter, there can be exchange of input or output between
        # the code running in that interpreter and code entered in another one.
        uid = threading.currentThread().getName()
        pageid = uid.split(":")[0]
        data = utilities.changeHTMLspecialCharacters(data)

        #Note: in the following, it is important to ensure that the
        # py_prompt class is surrounded by single quotes - not double ones.
        # normal prompt

        for _prompt in ['&gt;&gt;&gt; ', # normal prompt
                        '... ', # normal continuation prompt
                        '--&gt; ', # isolated prompt
                        '&lt;t&gt;&gt;&gt; ', # type info prompt
                        '_u__) ', # parrot
                        '_u__)) ' # Parrots
                        ]:
            dd = data.split('crunchy_py_prompt%s' % _prompt)
            data = ("<span class='py_prompt'>%s" % _prompt).join(dd)

        if self.__redirect(uid):
            output_buffers[pageid].put_output(("<span class='%s'>" % self.buf_class) + data + '</span>', uid)
        else:
            self.default_out.write(data.encode(sys.getfilesystemencoding()))

    def read(self):
        """N.B. this function is rarely, if ever, used - and is probably untested"""
        uid = threading.currentThread().getName()
        if self.__redirect(uid):
            #read the data
            data = input_buffers[uid].get()
        else:
            data = self.default_in.read()
        return data

    def readline(self):
        """used by Interactive Console - raw_input(">>>")"""

        uid = threading.currentThread().getName()
        new_id = "none"
        debug_msg("entering readline, uid=%s" % uid, 7)
        if self.__redirect(uid):
            new_id, data = input_buffers[uid].getline(uid)
        else:
            data = self.default_in.readline()
        debug_msg("leaving readline, uid=%s, new_id=%s\ndata=%s" % (uid,
                                                           new_id, data), 7)
        return data

    def __redirect(self, uid):
        """decide if the thread with uid uid should be redirected"""
        t = uid in input_buffers
        return t

    def default_write(self, data):
        """write to the default output"""
        self.default_out.write(data)

def debug_msg(data, id_=None):
    """write a debug message, debug messages always appear on stderr"""
    if id_ in debug_ids:
        sys.stderr.default_write(data + "\n")

sys.stdin = ThreadedBuffer(in_buf=sys.stdin)
sys.stdout = ThreadedBuffer(out_buf=sys.stdout, buf_class="stdout")
sys.stderr = ThreadedBuffer(out_buf=sys.stderr, buf_class="stderr")

reset_js = """
try{
document.getElementById("kill_%s").style.display="block";
}
catch(err){ ;}  //needed as the element may not exist.
document.getElementById("in_%s").style.display="inline";
document.getElementById("out_%s").innerHTML="";
"""
reset_js_3k = """
document.getElementById("in_{0}").style.display="inline";
document.getElementById("out_{1}").innerHTML="";
"""

help_js = """
document.getElementById("help_menu").style.display = "block";
document.getElementById("help_menu_x").style.display = "block";
"""
