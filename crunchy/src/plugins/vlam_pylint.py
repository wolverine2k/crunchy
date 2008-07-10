"""  Crunchy pylint plugin.

This is a proof of concept to analyze some code with pylint
"""

import os
import StringIO
import tempfile
try:
    from pylint import lint, checkers
    pylint_available = True
except ImportError:
    pylint_available = False

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, Element, SubElement, tostring
from src.utilities import extract_log_id, insert_markup

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget"])


class CrunchyLinter:
    """Class to configure and start a pylint analyze
    
    Based on the Run class from pylint.lint
    """
    
    def __init__(self, reporter=None, quiet=0, pylintrc=None):
        self.LinterClass = lint.PyLinter
        self._rcfile = pylintrc
        self.linter = self.LinterClass(reporter=reporter, pylintrc=self._rcfile)
        self.linter.quiet = quiet
        self._report = None
        # register standard checkers
        checkers.initialize(self.linter)
        ## Disable some errors
        #self.linter.disable_message('C0121')# required attribute "__revision__"
        #self.linter.disable_message('C0111')# required docstring (for the file)
        #self.linter.disable_message('C0103')# file name convention
        # read configuration
        self.linter.read_config_file()
        self.linter.load_config_file()
        if reporter:
            self.linter.set_reporter(reporter)
    
    def set_code(self, code):
        """Set the code to analyze"""
        self._code = """
'''Fake doctest for the analyze'''
__revision__ = 'nothing'
%(code)s
""" % {'code': code}
    
    def run(self):
        """Make the analyze"""
        # Save the code in a temporary file
        # TODO: should use the same temp directory than crunchy
        temp = tempfile.NamedTemporaryFile(suffix = '.py')
        temp.write(self._code)
        temp.flush()
        # Open a buffer for the output
        output_buffer = StringIO.StringIO()
        self.linter.reporter.set_output(output_buffer)
        # Start the check
        self.linter.check(temp.name)
        # Get the output
        self._report = output_buffer.getvalue()
        # Close files
        output_buffer.close()
        temp.close()
    
    def get_report(self):
        """Return the full report"""
        return self._report
    
    def get_global_note(self):
        """Return the global note
        
        This note can be formatted with "%.2f/10" % note
        """
        return self.linter.stats['global_note']


def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "run unittest" commands,
          issued by clicking on a button incorporated in the
          'unittest widget';
       """
    if pylint_available:
        # 'pylint' only appears inside <pre> elements, using the notation
        # <pre title='pylint ...'>
        plugin['register_tag_handler']("pre", "title", "pylint",
                                              pylint_widget_callback)
        # By convention, the custom handler for "name" will be called
        # via "/name"; for security, we add a random session id
        # to the custom handler's name to be executed.
        plugin['register_http_handler'](
                         "/pylint%s"%plugin['session_random_id'],
                                       pylint_runner_callback)


def pylint_runner_callback(request):
    """Handles all execution of pylint. The request object will contain
    all the data in the AJAX message sent from the browser."""
    linter = CrunchyLinter()
    linter.set_code(request.data)
    linter.run()
    request.send_response(200)
    request.end_headers()
    
    # Why this doesn't work!!
    #request.wfile.write(linter.get_report())
    #request.wfile.flush()
    
    # dirty hack
    plugin['exec_code']('print """Code quality %.2f/10\n%s"""' % \
        (linter.get_global_note(), linter.get_report()), request.args["uid"])
    

def pylint_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run pylint"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'pylint'
        config['logging_uids'][uid] = (log_id, t)
    
    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config['page_security_level'](page.url):
        if not page.includes("pylint_included") :
            page.add_include("pylint_included")
            page.add_js_code(pylint_jscode)
    
    # next, we style the code, also extracting it in a useful form ...
    pylintcode, markup, dummy = plugin['services'].style_pycode_nostrip(page, elem)
    if log_id:
        config['log'][log_id] = [tostring(markup)]
    # which we store
    #unittests[uid] = unittestcode

    insert_markup(elem, uid, vlam, markup, "unittest")

    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid)
    #some spacing:
    SubElement(elem, "br")
    # the actual button used for code execution:
    btn = SubElement(elem, "button")
    btn.text = "Run analyze"
    btn.attrib["onclick"] = "exec_pylint('%s')" % uid
    SubElement(elem, "br")
    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

# we need some unique javascript in the page; note how the
# "/pylint" handler mentioned above appears here, together with the
# random session id.
pylint_jscode = """
function exec_pylint(uid){
    document.getElementById("kill_image_"+uid).style.display = "block";
    code=editAreaLoader.getValue("code_"+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/pylint%s?uid="+uid, false);
    j.send(code);
};
""" % plugin['session_random_id']
