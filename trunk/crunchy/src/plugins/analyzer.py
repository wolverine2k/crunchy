"""  Crunchy analyzer plugin.

This is the frontend for analyzers like pylint
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, SubElement, tostring
from src.interface import translate, additional_vlam
from src.utilities import extract_log_id, wrap_in_div
import src.configuration as configuration
_ = translate['_']

# The set of other "widgets/services" provided by this plugin
provides = set(["analyzer_widget"])

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget"])

analyzer_names = [None]#{None: _("Disabled")}

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

    plugin['register_service']('insert_analyzer_button',
                               insert_analyzer_button)
    plugin['register_service']('add_scoring', add_scoring)
    plugin['register_service']('register_analyzer_name',
                               analyzer_names.append)

    # 'analyzer' only appears inside <pre> elements, using the notation
    # <pre title='analyzer ...'>
    plugin['register_tag_handler']("pre", "title", "analyzer",
                                   analyzer_widget_callback)
    # Register the 'get_analyzer' service
    plugin['register_service']('get_analyzer', get_analyzer)

def analyzer_enabled(username):
    """Return True if an analyzer is available and enabled"""
    return 'analyzer' in config[username] and config[username]['analyzer'] is not None

def get_analyzer(username):
    """Return the current analyzer (or None)"""
    if analyzer_enabled(username):
        return plugin['services'].__dict__['get_analyzer_%s' % \
                                           config[username]['analyzer']]

def analyzer_runner_callback(request):
    """Handles all execution of the analyzer to display a report.
    The request object will contain
    all the data in the AJAX message sent from the browser."""
    username = request.crunchy_username
    info = request.data.split("__SEPARATOR__")
    code = '__SEPARATOR__'.join(info[1:])
    # Get the choosen analyzer (if any)
    analyzer = info[0]
    if analyzer :
        # Change the config if needed
        if analyzer == str(None):
            analyzer = None
        if analyzer != config[username]['analyzer']:
            config[username]['analyzer'] = analyzer
            # need to save here?

    request.send_response(200)
    request.end_headers()
    uid = request.args["uid"]
    pageid = uid.split("_")[0]

    if analyzer_enabled(username):
        # Analyzer the code
        analyzer = plugin['services'].get_analyzer(username)
        #analyzer.set_code(code)
        analyzer.run(code)
        report = analyzer.get_report()
        plugin['append_text'](pageid, uid, '\n' + "="*60 + "\n")
        if report:
            plugin['append_text'](pageid, uid, report)
        else:
            plugin['append_text'](pageid, uid, _("Nothing to report."))
    else:
        plugin['append_text'](pageid, uid,
                              _("Please install and enable an analyzer."))

def analyzer_score_callback(request):
    """Handles all execution of the analyzer to display a score
    The request object will contain
    all the data in the AJAX message sent from the browser."""
    analyzer = get_analyzer(request.crunchy_username)
    analyzer.run(request.data)
    request.send_response(200)
    request.end_headers()
    uid = request.args["uid"]
    pageid = uid.split("_")[0]
    plugin['append_text'](pageid, uid, "\n")
    score = analyzer.get_global_score()
    if score is not None:
        if score > 0. :
            plugin['append_text'](pageid, uid,
                    _("[From %s, code quality: %.2f/10]\n") %
                        (config[request.crunchy_username]['analyzer'], score))
        else:
            plugin['append_text'](pageid, uid,
                    _("[From %s, code quality: 0]\n") %
                        config[request.crunchy_username]['analyzer'])

def analyzer_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run the analyzer"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'analyzer'
        config[page.username]['logging_uids'][uid] = (log_id, t)

    elem.attrib['title'] = "python"
    analyzercode, show_vlam = plugin['services'].style(page, elem, None, vlam)
    elem.attrib['title'] = vlam

    if log_id:
        config['log'][log_id] = [tostring(markup)]
    wrap_in_div(elem, uid, vlam, "analyzer", show_vlam)

    #insert_markup(elem, uid, vlam, markup, "analyzer")

    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid, analyzercode)
    #some spacing:
    SubElement(elem, "br")
    # use the insert_analyzer_button service as any plugin can do
    insert_analyzer_button(page, elem, uid)
    SubElement(elem, "br")
    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

def insert_analyzer_button(page, elem, uid):
    """inserts an Elementtree that is an button to make a report on the code
    quality.
    Return the inserted button
    """

    # Form to select the analyzer
    SubElement(elem, "br")
    form1 = SubElement(elem, 'form', name='form1_' + uid)
    span = SubElement(form1, 'span')
    span.text = _('Analyzer: ')
    span.attrib['class'] = 'analyzer'
    select = SubElement(form1, 'select', id='analyzer_'+uid)
    analyzer_names = configuration.options['analyzer']
    for name in analyzer_names:
        if name is None:
            analyzer = str(None)
        else:
            analyzer = name.replace('analyzer_', '')
        option = SubElement(select, 'option', value=analyzer)
        option.text = analyzer
        if analyzer == str(config[page.username]['analyzer']):
            option.attrib['selected'] = 'selected'
    SubElement(elem, "br")

    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("analyzer_included") :
            page.add_include("analyzer_included")
            page.add_js_code(analyzer_jscode)
    btn = SubElement(elem, "button")
    btn.text = _("Analyze the code")
    btn.attrib["onclick"] = "exec_analyzer('%s')" % uid
    # add the display of the score
    add_scoring(page, btn, uid)

def add_scoring(page, button, uid):
    """Add a call to the analyzer scoring function to a standard 'execute'
    button.
    """
    if analyzer_enabled(page.username):
        if 'display' not in config[page.username]['page_security_level'](page.url):
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
    analyzer = document.getElementById("analyzer_"+uid).value;
    j.send(analyzer+"__SEPARATOR__"+code);
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
