"""  Crunchy analyzer plugin.

This is the frontend for analyzers like pylint
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, SubElement, tostring
from src.interface import translate
from src.utilities import extract_log_id, insert_markup
_ = translate['_']

# The set of other "widgets/services" provided by this plugin
provides = set(["analyzer_widget"])

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. some custom http handler to deal with "run analyze" commands,
          issued by clicking on a button incorporated in the
          'analyzer widget';
       3. some services to let other plugin add analysis function.
       """
    
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler']("/analyzer%s"%plugin['session_random_id'],
                                    analyzer_runner_callback)
    plugin['register_http_handler'](
                            "/analyzer_score%s"%plugin['session_random_id'],
                            analyzer_score_callback)
    
    plugin['register_service']('insert_analyser_button',
                               insert_analyser_button)
    plugin['register_service']('add_scoring', add_scoring)
    
    # 'analyzer' only appears inside <pre> elements, using the notation
    # <pre title='analyzer ...'>
    plugin['register_tag_handler']("pre", "title", "analyzer",
                                   analyzer_widget_callback)

def analyzer_enabled():
    """Return is a analyzer is available and enable"""
    # TODO: Maybe this should check a configuration option
    return hasattr(plugin['services'], 'insert_analyser_button')

def analyzer_runner_callback(request):
    """Handles all execution of the analyzer to display a report.
    The request object will contain
    all the data in the AJAX message sent from the browser."""
    analyzer = plugin['services'].get_analyzer()
    analyzer.set_code(request.data)
    analyzer.run()
    request.send_response(200)
    request.end_headers()
    uid = request.args["uid"]
    pageid = uid.split(":")[0]
    plugin['append_html'](pageid, uid, analyzer.get_report())

def analyzer_score_callback(request):
    """Handles all execution of the analyzer to display a score
    The request object will contain
    all the data in the AJAX message sent from the browser."""
    analyzer = plugin['services'].get_analyzer()
    analyzer.set_code(request.data)
    analyzer.run()
    request.send_response(200)
    request.end_headers()
    uid = request.args["uid"]
    pageid = uid.split(":")[0]
    plugin['append_html'](pageid, uid, "\n")
    plugin['append_html'](pageid, uid, _("[Code quality %.2f/10]\n") % \
                          analyzer.get_global_score())

def analyzer_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run the analyzer"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'analyzer'
        config['logging_uids'][uid] = (log_id, t)
    
    # next, we style the code, also extracting it in a useful form ...
    analyzercode, markup, dummy = plugin['services'].style_pycode_nostrip(page,
                                                                        elem)
    if log_id:
        config['log'][log_id] = [tostring(markup)]
    
    insert_markup(elem, uid, vlam, markup, "analyzer")
    
    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid, analyzercode)
    #some spacing:
    SubElement(elem, "br")
    if analyzer_enabled():
        # use the insert_analyser_button service as any plugin can do
        plugin['services'].insert_analyser_button(page, elem, uid)
    else:
        # Display a nice link
        pylint_link = SubElement(elem, "a")
        pylint_link.text = _("You need to install an analyzer such as pylint")
        pylint_link.attrib["href"] = "http://www.logilab.org/857"
    SubElement(elem, "br")
    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

def insert_analyser_button(page, elem, uid):
    """inserts an Elementtree that is an button to make a report on the code
    quality.
    Return the inserted button
    """
    if analyzer_enabled():
        if 'display' not in config['page_security_level'](page.url):
            if not page.includes("analyzer_included") :
                page.add_include("analyzer_included")
                page.add_js_code(analyzer_jscode)
        btn = SubElement(elem, "button")
        btn.text = _("Analyze the code")
        btn.attrib["onclick"] = "exec_analyzer('%s')" % uid
        # add the display of the score
        plugin['services'].add_scoring(page, btn, uid)
        return btn
    else:
        return None

def add_scoring(page, button, uid):
    """Add a call to the analyzer scoring function to a standard 'execute'
    button.
    """
    if analyzer_enabled():
        if 'display' not in config['page_security_level'](page.url):
            if not page.includes("analyzer_score_included") :
                page.add_include("analyzer_score_included")
                page.add_js_code(analyzer_score_jscode)
        button.attrib["onclick"] += " ; exec_analyzer_score('%s')" % uid

# we need some unique javascript in the page; note how the
# "/analyzer" handler mentioned above appears here, together with the
# random session id.
analyzer_jscode = """
function exec_analyzer(uid){
    document.getElementById("kill_image_"+uid).style.display = "block";
    code=editAreaLoader.getValue("code_"+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/analyzer%s?uid="+uid, false);
    j.send(code);
};
""" % plugin['session_random_id']
analyzer_score_jscode = """
function exec_analyzer_score(uid){
    code=editAreaLoader.getValue("code_"+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/analyzer_score%s?uid="+uid, false);
    j.send(code);
};
""" % plugin['session_random_id']
