"""  Crunchy pdb plugin.
Debugger In Browser
Features:
    next
    step
    return
    show local namespace  (highlight just changed or newly create name)
    highlight current line (can jump between files)
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, SubElement, tostring, translate
from src.utilities import extract_log_id, unChangeHTMLspecialCharacters, escape_for_javascript
import src.utilities as util
from src.cometIO import raw_push_input, extract_data, is_accept_input, write_output
import re, sys

_ = translate['_']

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget", "register_io_hook"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "exec pdb command" commands,
       """
    # 'pdb' only appears inside <pre> elements, using the notation
    # <pre title='pdb ...'>
    plugin['register_tag_handler']("pre", "title", "pdb",
                                          pdb_widget_callback)
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler'](
                         "/pdb_cmd%s"%plugin['session_random_id'],
                         pdb_command_callback)

    plugin['register_http_handler'](
                         "/pdb_start%s"%plugin['session_random_id'],
                        pdb_start_callback)

    plugin['register_http_handler'](
                         "/pdb_js%s.js"%plugin['session_random_id'],
                        pdb_js_file_callback)


pdb_py_files = {}

def pdb_start_callback(request):
    pdb_py_files[request.args['uid']]['<string>'] = request.data
    code = pdb_pycode % (request.data.replace('""""', r'\"\"\"'))
    plugin['exec_code'](code, request.args["uid"])
    request.send_response(200)
    request.end_headers()

def pdb_command_callback(request):
    """Handles all pdb command. The request object will contain
    all the data in the AJAX message sent from the browser."""
    # note how the code to be executed is not simply the code entered by
    # the user, and obtained as "request.data", but also includes a part
    # (doctest_pycode) defined below used to automatically call the
    # correct method in the doctest module.
    uid = request.args["uid"]
    command = request.args["command"]
    if command == "next":
        raw_push_input(uid, "next\n")
        raw_push_input(uid, "crunchy_update_page\n")
    elif command == "step":
        raw_push_input(uid, "step\n")
        raw_push_input(uid, "crunchy_update_page\n")
    elif command == "return":
        raw_push_input(uid, "return\n")
        raw_push_input(uid, "crunchy_update_page\n")
    request.send_response(200)
    request.end_headers()


def pdb_filter(data, uid):
    '''modifify the output of pdb command'''
    page_id = uid.split('_')[0]
    buff_class,text = extract_data(data)
    proto = Proto()
    if buff_class == "stdout":
        text = unChangeHTMLspecialCharacters(text)
        command, d = proto.decode(text)
        if command is None:
            pass
        elif command == 'crunchy_locals':
            plugin['exec_js'](page_id, "window['pdb_%s'].update_local_ns('%s');" %(uid, escape_for_javascript(d)))
            data = ""
        elif command == 'crunchy_where':
            filename,line_no = d.split('|')
            if filename not in pdb_py_files[uid]:
                try:
                    content = open(filename).read()
                    pdb_py_files[uid][filename] = content
                except IOError:
                    content = "#SORRY, SOURCE NOT AVAILABLE"
            else:
                content = ""
            filename = escape_for_javascript(filename)
            content = escape_for_javascript(content)
            plugin['exec_js'](page_id, "window['pdb_%s'].go_to_file_and_line('%s','%s','%s');" %(uid, filename, content, line_no))
            data = ""
        elif command == "crunchy_finished":
            plugin['exec_js'](uid.split('_')[0], "window['pdb_%s'].on_terminate();" %(uid))
            plugin['exec_js'](uid.split('_')[0], "alert('" + _("Reached the end of the code.") + "');")
            data = ""
    elif buff_class == "stdin":
        #no echo at all
        data = ""
    return data

def pdb_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run pdb"""

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("pdb_included"):
            page.add_include("pdb_included")
            #element tree always escape < to &lt; and break my js code , so...
            page.insert_js_file("/pdb_js%s.js"%plugin['session_random_id'])
        if not page.includes("pdb_css_code"):
            page.add_include("pdb_css_code")
            page.add_css_code(pdb_css)
    # next, we style the code, also extracting it in a useful form ...

    vlam = elem.attrib["title"]
    python_code = util.extract_code(elem)
    if util.is_interpreter_session(python_code):
        elem.attrib['title'] = "pycon"
        python_code = util.extract_code_from_interpreter(python_code)
    else:
        elem.attrib['title'] = "python"
    code, show_vlam = plugin['services'].style(page, elem, None, vlam)
    elem.attrib['title'] = vlam
    util.wrap_in_div(elem, uid, vlam, "pdb", show_vlam)

    plugin['services'].insert_editor_subwidget(page, elem, uid, python_code)

    t = SubElement(elem, "h4")
    t.text = _("Local Namespace")
    local_ns_div = SubElement(elem, "div")
    local_ns_div.attrib["id"] = "local_ns_%s"%uid

    #some spacing:
    SubElement(elem, "br")

    btn = SubElement(elem, "button")
    btn.text = _("Start PDB")
    btn.attrib["onclick"] = "init_pdb('%s');" %(uid)
    btn.attrib["id"] = "btn_start_pdb_%s" % uid

    btn = SubElement(elem, "button")
    btn.text = _("Next Step")
    btn.attrib["id"] = "btn_next_step_%s" % uid
    btn.attrib["disabled"] = "disabled"

    btn = SubElement(elem, "button")
    btn.text = _("Step Into")
    btn.attrib["id"] = "btn_step_into_%s" % uid
    btn.attrib["disabled"] = "disabled"

    btn = SubElement(elem, "button")
    btn.text = _("Return")
    btn.attrib["id"] = "btn_return_%s" % uid
    btn.attrib["disabled"] = "disabled"

    SubElement(elem, "br")

    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

    #register before_ouput hook
    plugin['services'].register_io_hook('before_output', pdb_filter, uid)

    #create pdb file cache for uid
    pdb_py_files[uid] = {}

def pdb_js_file_callback(request):
    request.send_response(200)
    request.end_headers()
    request.wfile.write(pdb_jscode)


pdb_css = r"""
table.namespace td{
    border: 1px solid rgb(170, 170, 170); padding: 5px;
}
table.namespace tr.modified {
    background-color:red;
}
table.namespace tr.new {
    background-color:yellow;
}
"""
pdb_jscode = r"""
var random_session_id = '%s';

function pdb_interpreter(uid)
{
    this.uid = uid;
    this._local_var = {};
    this._global_var = {};
}


pdb_interpreter.prototype = {
    init : function(){
        uid = this.uid;
        var j = new XMLHttpRequest();
        code = document.getElementById('code_' + uid).value;
        j.open("POST", "/pdb_start" + random_session_id + "?uid="+uid, false);
        j.send(code);

        //bind events
        var _this = this;
        self.start_btn = document.getElementById('btn_start_pdb_' + uid);//.disabled= true;
        self.next_step_btn = document.getElementById('btn_next_step_' + uid);
        self.step_into_btn = document.getElementById('btn_step_into_' + uid);
        self.return_btn = document.getElementById('btn_return_' + uid);
        self.show_local_var_btn = document.getElementById('btn_show_local_var_' + uid);
        self.next_step_btn.onclick = function(){ _this.send_cmd('next')};
        self.step_into_btn.onclick = function(){ _this.send_cmd('step')};
        self.return_btn.onclick = function(){ _this.send_cmd('return')};
        //self.show_local_var_btn.onclick = function(){ _this.send_cmd('local_var')};

        //enable them
        self.start_btn.disabled = true;
        self.next_step_btn.disabled = false;
        self.step_into_btn.disabled = false;
        self.return_btn.disabled = false;
        //self.show_local_var_btn.disabled = false;

        //clean local var table
        this.update_local_ns("");

        this.files = {};
        this.files['<string>'] = {'content' : eAL.getValue("code_" + uid), 'curr_line' : 1};
        this.current_file = '<string>';
    },
    on_terminate : function(){
        self.start_btn.disabled = false;
        self.next_step_btn.disabled = true;
        self.step_into_btn.disabled = true;
        self.return_btn.disabled = true;
        this.update_local_ns("");
    },
    send_cmd : function(cmd){
        uid = this.uid;
        var j = new XMLHttpRequest();
        //j.open("POST", "/pdb_" + cmd + random_session_id +"?uid="+uid, false);
        j.open("POST", "/pdb_cmd"+ random_session_id +"?uid="+uid + "&command=" + cmd, false);
        j.send(cmd + "\n");
    },
    //update local namespace , update the html
    update_local_ns: function(data){
        var uid = this.uid;
        var container = document.getElementById('local_ns_' + uid);
        container.innerHTML = data;
    },
    //update global namespace , update the html
    update_global_ns: function(data){
        var uid = this.uid;
        var container = document.getElementById('global_ns_' + uid);
        container.innerHTML = data;
    },
    go_to_file_and_line : function(file_name, content, line_no){
        var uid = this.uid;
        this.current_file = file_name;
        if (!this.files[file_name])
        {
            this.files[file_name] = {'content' : content, 'curr_line' : line_no};
        }
        else
        {
            this.files[file_name]['curr_line'] = line_no;
        }
        eAL.setValue("code_" + uid, this.files[this.current_file]['content']);
        this.move_to_line(line_no);
    },
    //move the curse to line <line> and highlight it
    //assume we are using edit area
    move_to_line: function(line){
        var uid = this.uid;
        var content = eAL.getValue("code_" + uid);
        var i = 1;
        var start = 0;
        while(i < line)
        {
            start = content.indexOf('\n', start) + 1;
            i ++;
        }
        end = content.indexOf('\n', start);
        if(line > 11)
        {
            t = document.getElementById("code_" + uid);
            t.scrollTop = (line -4)*t.clientHeight/11;
        }
        eAL.setSelectionRange("code_" + uid, start, end);
    }
}

function init_pdb(uid)
{
    window['pdb_' + uid] = new pdb_interpreter(uid);
    window['pdb_' + uid].init();
}
""" % (plugin['session_random_id'])

pdb_pycode = '''
from src.plugins.vlam_pdb import MyPdb,Proto
_debug_string = """%s
"""
mypdb = MyPdb()
mypdb.run(_debug_string, globals={}, locals={})
mypdb.c_stdout.write(Proto().encode('crunchy_finished', '---FINISHED---'))
'''

from pdb import Pdb
from StringIO import StringIO
import inspect

class Proto:
    '''Proto used to encode and decode information between mypdb and crunchy'''

    def __init__(self):
        self.prefix = "___CRUNCHY_PDB_START__"
        self.suffix = "___CRUNCHY_PDB_END__"

    def encode(self, command, data):
        return '\n'.join((self.prefix, command, data, self.suffix))

    def decode(self, msg):
        if not msg.startswith(self.prefix):
            return (None, msg)
        else:
            prefix, command, data = msg.split('\n',2)
            data = data[:data.find(self.suffix)-1]
            return (command, data)

class MyStringIO(StringIO):
    '''Eat Up Every thing'''

    def __init__(self, old_out):
        self.old_out = old_out
        StringIO.__init__(self)

    def write(self, data):
        pass
        #self.old_out.write("data = %s\n" %data)
        #self.old_out.write(str(outer_frames) + "\n--------------------\n")


class MyPdb(Pdb):

    def __init__(self):
        Pdb.__init__(self)
        self.proto = Proto()
        self.c_stdout = self.stdout #crunchy output
        self.stdout =  MyStringIO(self.stdout)  #eat up everything output by orginal pdb
        self.prompt = "" #remove prompt
        self.use_rawinput = 0

        #these name should not be exposed to user (as they are used by pdb)
        self.exclude_name_list = ['__return__', '__exception__']#, '__builtins__']

        self.last_locals = {}

    def get_name_id_map(self, d):
        ret = {}
        for key,item in d.items():
            ret[key] = id(item)
        return ret

    def filter_dict(self, d):
        ret = {}
        for key,value in d.items():
            if key not in self.exclude_name_list:
                ret[key] = value
        return ret

    def do_output_off(self, arg = None):
        '''do command and capture the output'''
        self.old_stdout = self.stdout
        self.stdout = StringIO()

    def do_output_on(self, arg = None):
        self.stdout = self.old_stdout

    def do_crunchy_next(self, arg = None):
        '''Crunchy Next , do next and send other command to communicate with crunchy'''
        self.do_next(arg)
        return True

    def do_crunchy_step(self, arg = None):
        '''Crunchy Step, do step and send other command to communicate with crunchy'''
        self.do_step(arg)
        return True

    def do_crunchy_return(self, arg = None):
        '''Crunchy Return , do return and send other command to communicate with crunchy'''
        self.do_return(arg)
        return True

    def do_crunchy_update_page(self, arg = None):
        self.do_crunchy_locals(arg)
        self.do_crunchy_where(arg)

    def do_crunchy_where(self, arg = None):
        '''Get current module and lineno'''
        self.last_frame = self.curframe
        for frame_lineno in self.stack:
            frame,lineno = frame_lineno
            if frame is self.curframe:
                filename = self.canonic(frame.f_code.co_filename)
                self.c_stdout.write(self.proto.encode('crunchy_where', '|'.join((filename, str(lineno)))))
                break

    def dict2table(self, d, old = {}):
        s = "<table class='namespace'><tbody>"
        for key,item in d.items():
            t = "normal"
            if key not in old:
                t = "new"
            elif id(item) != old[key]:
                t = "modified"
            item = str(item).replace('<', '&lt;')
            s += "<tr class='%s'><td>%s</td><td>%s</td></tr>\n" %(t, str(key), str(item))
        s += "</tbody></table>"
        return s

    def do_crunchy_locals(self, arg):
        '''Get local namespace and format it as an html table'''
        locals = self.filter_dict(self.curframe.f_locals)
        old = self.last_locals.get(id(self.curframe), {})
        self.c_stdout.write(self.proto.encode('crunchy_locals', self.dict2table(locals, old)))
        self.last_locals[id(self.curframe)] = self.get_name_id_map(locals)

    def do_crunchy_globals(self, arg):
        '''Get local namespace and format it as an html table'''
        globals = self.filter_dict(self.curframe.f_globals)
        self.c_stdout.write(self.proto.encode('crunchy_globals', self.dict2table(globals)))
