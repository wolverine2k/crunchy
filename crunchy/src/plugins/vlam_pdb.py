"""  Crunchy pdb plugin.

Pdb the code in the pre area

"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, SubElement, tostring
from src.utilities import extract_log_id,unChangeHTMLspecialCharacters,escape_for_javascript
import src.session as session
from src.cometIO import raw_push_input,extract_data
import re,sys

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget", "register_io_hook"])


def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "exec pdb command" commands,
       """
    # 'doctest' only appears inside <pre> elements, using the notation
    # <pre title='doctest ...'>
    plugin['register_tag_handler']("pre", "title", "pdb",
                                          pdb_widget_callback)
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler'](
                         "/pdb_next%s"%plugin['session_random_id'],
                         lambda r :pdb_command_callback(r, "next"))

    plugin['register_http_handler'](
                         "/pdb_step%s"%plugin['session_random_id'],
                         lambda r :pdb_command_callback(r, "step"))

    plugin['register_http_handler'](
                         "/pdb_return%s"%plugin['session_random_id'],
                         lambda r :pdb_command_callback(r, "return"))

    #plugin['register_http_handler'](
    #                     "/pdb_local_var%s"%plugin['session_random_id'],
    #                     lambda r :pdb_command_callback(r, "local_var"))

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
    #(pdb_codes[request.args["uid"]])
    plugin['exec_code'](code, request.args["uid"])
    request.send_response(200)
    request.end_headers()

def pdb_command_callback(request, command = "next"):
    """Handles all pdb command. The request object will contain
    all the data in the AJAX message sent from the browser."""
    # note how the code to be executed is not simply the code entered by
    # the user, and obtained as "request.data", but also includes a part
    # (doctest_pycode) defined below used to automatically call the
    # correct method in the doctest module.
    uid = request.args["uid"]
    if command == "next":
        #raw_push_input(uid, "output_off\n")
        raw_push_input(uid, "next\n")
        #raw_push_input(uid, "output_on\n")
        raw_push_input(uid, "crunchy_update_page\n")
    #elif command == "local_var":
    #    raw_push_input(uid, "simple_where\n")
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
    buff_class,text = extract_data(data)
    proto = Proto()
    if buff_class == "stdout":
        text = unChangeHTMLspecialCharacters(text)
        command, d = proto.decode(text)
        if command is None:
            pass
        elif command == 'crunchy_locals':
            plugin['exec_js'](plugin['get_pageid'](), "window['pdb_%s'].update_local_ns('%s');" %(uid, escape_for_javascript(d)))
            data = ""
        elif command == 'crunchy_globals':
            plugin['exec_js'](plugin['get_pageid'](), "window['pdb_%s'].update_global_ns('%s');" %(uid, escape_for_javascript(d)))
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
            plugin['exec_js'](plugin['get_pageid'](), "window['pdb_%s'].go_to_file_and_line('%s','%s','%s');" %(uid, filename, content, line_no))
            data = ""
    elif buff_class == "stdin":
        #no echo at all
        data = ""
    #no normal output at all
    return data

def pdb_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run pdb"""
    vlam = elem.attrib["title"]
    #logging this is meanless
    #log_id = extract_log_id(vlam)
    #if log_id:
    #    t = 'doctest'
    #    session.add_log_id(uid, log_id, t)
        #config['logging_uids'][uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config['page_security_level'](page.url):
        if not page.includes("pdb_included"):
            page.add_include("pdb_included")
            #element tree always escape < to &lt; and break my js code , so...
            page.insert_js_file("/pdb_js%s.js"%plugin['session_random_id'])
        if not page.includes("pdb_css_code"):
            page.add_include("pdb_css_code")
            page.add_css_code(pdb_css)
    # next, we style the code, also extracting it in a useful form ...
    code, markup, dummy = plugin['services'].style_pycode_nostrip(page, elem)
    # which we store
    # reset the original element to use it as a container.  For those # familiar with dealing with ElementTree Elements, in other context, # note that the style_pycode_nostrip() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    # We insert the styled doctest code inside this container element:
    #elem.insert(0, markup)
    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid, code)

    t = SubElement(elem, "h4")
    t.text = "Local Namespace"
    local_ns_div = SubElement(elem, "div")
    local_ns_div.attrib["id"] = "local_ns_%s"%uid 

    #t = SubElement(elem, "h4")
    #t.text = "Global Namespace"
    #global_ns_div = SubElement(elem, "div")
    #global_ns_div.attrib["id"] = "global_ns_%s"%uid 

    #some spacing:
    SubElement(elem, "br")

    btn = SubElement(elem, "button")
    btn.text = "Start PDB"
    btn.attrib["onclick"] = "init_pdb('%s');" %(uid)
    btn.attrib["id"] = "btn_start_pdb_%s" % uid

    btn = SubElement(elem, "button")
    btn.text = "Next Step"
    btn.attrib["id"] = "btn_next_step_%s" % uid
    btn.attrib["disabled"] = "disabled"

    btn = SubElement(elem, "button")
    btn.text = "Step Into"
    btn.attrib["id"] = "btn_step_into_%s" % uid
    btn.attrib["disabled"] = "disabled"

    btn = SubElement(elem, "button")
    btn.text = "return"
    btn.attrib["id"] = "btn_return_%s" % uid
    btn.attrib["disabled"] = "disabled"

    #btn = SubElement(elem, "button")
    #btn.text = "Show Local Var"
    #btn.attrib["id"] = "btn_show_local_var_%s" % uid
    #btn.attrib["disabled"] = "disabled"

    SubElement(elem, "br")

    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)
    

    #retister before_ouput hook
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
    color:red;
}
table.namespace tr.new {
    color:green;
}
div.btns {
    
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
    send_cmd : function(cmd){
        uid = this.uid;
        var j = new XMLHttpRequest();
        j.open("POST", "/pdb_" + cmd + random_session_id +"?uid="+uid, false);
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
from src.plugins.vlam_pdb import MyPdb
_debug_string = """%s
"""
MyPdb().run(_debug_string, globals={}, locals={})
'''

from pdb import Pdb
from StringIO import StringIO

class Proto:
    '''Proto used to encode and decond information between mypdb and crunchy'''

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

class MyPdb(Pdb):

    def __init__(self):
        Pdb.__init__(self) 
        self.proto = Proto()

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
        #self.do_crunchy_globals(arg)
        self.do_crunchy_where(arg)

    def do_crunchy_where(self, arg = None):
        '''Get current module and lineno'''
        for frame_lineno in self.stack:
            frame,lineno = frame_lineno
            if frame is self.curframe:
                filename = self.canonic(frame.f_code.co_filename)
                print >>self.stdout, self.proto.encode('crunchy_where', '|'.join((filename, str(lineno))))
                break

    #def dict2table(self, d, old = {}):
    def dict2table(self, d):
        s = "<table class='namespace'>"
        #s += "<thead><tr><th>name</th><th>value</th></tr></thead>"
        s += "<tbody>"
        for key,item in d.items():
            t = "normal"
            #if key not in old:
            #    t = "new"
            #elif id(item) is id(old[key]):
            #    t = "unchange"
            #else:
            #    t = "modified"
            item = str(item).replace('<', '&lt;')
            s += "<tr class='%s'><td>%s</td><td>%s</td></tr>\n" %(t, str(key), str(item))
        s += "</tbody>"
        s += "</table>"
        return s
    
    def do_crunchy_locals(self, arg):
        '''Get local nanespace and format it a html table'''
        locals = self.curframe.f_locals
        print >>self.stdout, self.proto.encode('crunchy_locals', self.dict2table(locals))
        #try:
        #    old = self.last_locals
        #except AttributeError,e:
        #    old = {} 
        #self.last_locals = locals

    def do_crunchy_globals(self, arg):
        '''Get local nanespace and format it a html table'''
        globals = self.curframe.f_globals
        print >>self.stdout, self.proto.encode('crunchy_globals', self.dict2table(globals))

