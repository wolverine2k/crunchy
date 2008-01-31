'''doc_code_check.py

Plugin designed to perform automatic checks on Python code included in
documentation.  It can handle the case where the Python code has to
be run with some pre-condition, and compares the actual output with
some expected output.'''

import copy
import difflib
import re
import sys

from src.interface import StringIO, plugin, config, Element, SubElement
import src.imports.dhtml as dhtml

code_setups = {}
code_samples = {}
expected_outputs = {}
names = {}

def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. three custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "run doctest" commands,
          issued by clicking on a button incorporated in the
          'doctest widget';
       """
    # 'doctest' only appears inside <pre> elements, using the notation
    # <pre title='doctest ...'>
    plugin['register_tag_handler']("pre", "title", "setup_code",
                                          code_setup_process)
    plugin['register_tag_handler']("pre", "title", "check_code",
                                          code_sample_process)
    plugin['register_tag_handler']("pre", "title", "code_output",
                                          expected_output_process)
    plugin['register_http_handler']("/check_code", doc_code_check_callback)

FAKE_UID = 0
FAKE_PAGEID = 0
def dummy_pageid():
    '''used to simulate a function that returns a pageid'''
    return FAKE_PAGEID

def dummy_uid():
    '''used to simulate a function that returns a uid'''
    return FAKE_UID

def doc_code_check_callback(request):
    '''execute the required test code, with setup code prepended,
    and compare with expected output'''
    global FAKE_UID, FAKE_PAGEID
    FAKE_UID = uid = request.args["uid"]
    FAKE_PAGEID = uid.split(":")[0]
    # save original values
    _get_pageid = plugin['get_pageid']
    _get_uid = plugin['get_uid']
    plugin['get_uid'] = dummy_uid
    plugin['get_pageid'] = dummy_pageid

    name = names[uid]
    #script = ["code_setups = {%s:%s}"%(name, code_setups[name]),
    #          "code_samples = {%s:%s}"%(name, code_samples[name]),
    #          "expected_outputs = {%s:%s}"%(name, expected_outputs[name]),
    #          "from src.plugins.doc_code_check import run_sample",
    #          "run_sample('%s')"%name]
    result = run_sample(name)
    #plugin['exec_code']('print """%s"""\n'%result, uid)
    if result == "Checked!":
        dhtml.image("/ok.png", width=16, height=16)
    else:
        #dhtml.image("/warning.png", width=16, height=16)
        plugin['exec_code']('print """%s"""\n'%result, uid)
    request.send_response(200)
    request.end_headers()
    # restore original values
    plugin['get_uid'] = _get_uid
    plugin['get_pageid'] = _get_pageid

def code_setup_process(page, elem, uid):
    """Style and saves a copy of the setup code"""
    vlam = elem.attrib["title"]
    name = extract_name(vlam)
    # next, we style the code, also extracting it in a useful form
    setup_code, markup, error = plugin['services'].style_pycode(page, elem)
    if error is not None:
        markup = copy.deepcopy(elem)
    # which we store
    code_setups[name] = setup_code
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_pycode() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = "crunchy"
    # We insert the styled setup code inside this container element:
    elem.append(markup)
    # Create a title
    h4 = Element('h4')
    h4.text = "Setup code; name= %s" % name
    elem.insert(0, h4)

def code_sample_process(page, elem, uid):
    """Style and saves a copy of the sample code"""
    vlam = elem.attrib["title"]
    name = extract_name(vlam)
    names[uid] = name
    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config['page_security_level'](page.url):
        if not page.includes("code_test_included") :
            page.add_include("code_test_included")
            page.add_js_code(code_test_jscode)
    # next, we style the code, also extracting it in a useful form
    sample_code, markup, error = plugin['services'].style_pycode(page, elem)
    if error is not None:
        markup = copy.deepcopy(elem)    # which we store
    code_samples[name] = sample_code
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_pycode() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = "crunchy"
    # We insert the styled sample code inside this container element:
    elem.append(markup)
    # Create a title
    h4 = Element('h4')
    h4.text = "Sample code; name= %s" % name
    elem.insert(0, h4)
    #some spacing:
    SubElement(elem, "br")
    # the actual button used for code execution:
    btn = SubElement(elem, "button")
    btn.text = "Run code check"
    btn.attrib["onclick"] = "exec_code_check('%s')" % uid
    SubElement(elem, "br")
    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

def expected_output_process(dummy, elem, uid):
    """Displays and saves a copy of the expected output"""
    vlam = elem.attrib["title"]
    name = extract_name(vlam)
    expected_output = elem.text
    # We assume that the author has written the expected output as
    # <pre ...>
    # starts on this line...
    # </pre>
    # When doing so, the newline at the end of the opening <pre...> needs
    # to be discarded so that it can be compared with the real output.
    if expected_output.startswith("\r\n"):
        expected_output = expected_output[2:]
    elif expected_output.startswith("\n\r"):
        expected_output = expected_output[2:]
    elif expected_output.startswith("\n"):
        expected_output = expected_output[1:]
    # which we store
    expected_outputs[name] = expected_output
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_pycode() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = "crunchy"
    # Create a title
    h4 = SubElement(elem, 'h4')
    h4.text = "Expected output; name= %s" % name
    # a container with the expected output
    pre = SubElement(elem, "pre")
    pre.text = expected_output

def run_sample(name):
    '''Given a setup script, as a precursor, executes a code sample
    and compares the output with some expected result.'''
    if name in code_setups:
        try:
            complete_code = code_setups[name] + '\n' + code_samples[name]
        except KeyError:
            sys.__stderr__.write("There was an error in run_sample().")
    else:
        try:
            complete_code = code_samples[name]
        except KeyError:
            sys.__stderr__.write("There was an error in run_sample.")
    saved_stdout = sys.stdout # Crunchy often redefines sys.stdout
    redirected = StringIO()
    sys.stdout = redirected
    exec(complete_code)
    sys.stdout = saved_stdout
    return compare(expected_outputs[name], redirected.getvalue())

def compare(s1, s2):
    '''compares two strings for equality'''
    t1 = s1.splitlines()
    t2 = s2.splitlines()
    d = difflib.Differ()
    comparison = list(d.compare(t1, t2))
    result = "Checked!"
    for line in comparison:
        if not line.startswith(' '):
            result = '\n'.join(comparison)
            break
    return result

name_pattern = re.compile("name\s*=\s*([a-zA-Z0-9_]+)")
def extract_name(vlam):
    '''extracts the value of name in a vlam title attribute'''
    # assume vlam is something like "some_keyword junk name=some_name"
    # possibly with some spaces around the equal sign
    result = name_pattern.search(vlam)
    return result.groups()[0]

# we need some unique javascript in the page; note how the
# /code_test handler mentioned above appears here, together with the
# random session id.
code_test_jscode = """
function exec_code_check(uid){
    var j = new XMLHttpRequest();
    j.open("POST", "/check_code?uid="+uid, false);
    j.send('');
};
"""