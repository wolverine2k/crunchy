'''doc_code_check.py:  unit tests in test_doc_code_check.rst

Plugin designed to perform automatic checks on Python code included in
documentation.  It can handle the case where the Python code has to
be run with some pre-condition, and compares the actual output with
some expected output.'''

import copy
import difflib
import re
import sys

from src.interface import StringIO, plugin, config, Element, SubElement
from src.utilities import append_checkmark, append_warning

code_setups = {}
code_samples = {}
expected_outputs = {}
names = {}

css = u"""
.test_output{background-color:#ccffcc}
.test_setup{background-color:#bbccff}
"""

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

    # Commenting out due to reliance on the colourize plugin.
    # plugin['register_tag_handler']("pre", "title", "setup_code",
    #                                       code_setup_process)
    # plugin['register_tag_handler']("pre", "title", "check_code",
    #                                       code_sample_process)

    plugin['register_tag_handler']("pre", "title", "code_output",
                                          expected_output_process)
    plugin['register_http_handler']("/check_code", doc_code_check_callback)
    plugin['register_http_handler']("/check_all_code_samples",
                                    all_code_samples_check_callback)

class MockPageInfo(object):
    '''used to mock information normally obtained from a vlam page'''
    fake_uid = 0
    fake_pageid = 0
    saved_get_pageid = None
    saved_get_uid = None

    def dummy_pageid(self):
        '''used to simulate a function that returns a pageid'''
        return str(self.fake_pageid)

    def dummy_uid(self):
        '''used to simulate a function that returns a uid'''
        return str(self.fake_uid)

    def set(self):
        '''redirects the normal page functions to use the fake ones'''
        self.saved_get_pageid = plugin['get_pageid']
        self.saved_get_uid = plugin['get_uid']
        plugin['get_uid'] = mock_page.dummy_uid
        plugin['get_pageid'] = mock_page.dummy_pageid

    def restore(self):
        '''restore the normal page functions to their normal values'''
        plugin['get_uid'] = self.saved_get_uid
        plugin['get_pageid'] = self.saved_get_pageid

mock_page = MockPageInfo()

def all_code_samples_check_callback(request):
    '''tests all the code samples on a given page'''
    pageid = request.args["pageid"]
    failed = False
    for uid in names:
        if uid.startswith(pageid+":"):
            result = do_single_test(pageid, uid)
            if result == 'Failed':
                failed = True
    if failed:
        append_warning(pageid, "btn1_"+pageid)
        append_warning(pageid, "btn2_"+pageid)
    else:
        append_checkmark(pageid, "btn1_"+pageid)
        append_checkmark(pageid, "btn2_"+pageid)
    request.send_response(200)
    request.end_headers()


def doc_code_check_callback(request):
    '''execute the required test code, with setup code prepended,
    and compare with expected output'''
    uid = request.args["uid"]
    pageid = uid.split("_")[0]
    dummy = do_single_test(pageid, uid)
    request.send_response(200)
    request.end_headers()

def do_single_test(pageid, uid):
    '''runs a single test and updates the page to indicate the result'''
    name = names[uid]
    result = run_sample(name)
    if result == "Checked!":
        append_checkmark(pageid, "div_"+uid)
        return None
    else:
        append_warning(pageid, "div_"+uid)
        mock_page.fake_uid = uid
        mock_page.fake_pageid = pageid
        mock_page.set()
        plugin['exec_code']('print """%s"""\n'%result, uid)
        mock_page.restore()
        return 'Failed'

def code_setup_process(page, elem, uid):
    """Style and saves a copy of the setup code. This code currently
    does not work because it depends on the obsoleted style_pycode
    service in the colourize plugin."""

    raise NotImplementedError()

    vlam = elem.attrib["title"]
    name = extract_name(vlam)
    # next, we style the code, also extracting it in a useful form
    setup_code, markup, error = plugin['services'].style_pycode(page,
                                                   elem, css_class='test_setup')
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
    elem.attrib["id"] = "div_" + uid
    elem.attrib['class'] = "test_setup"
    # We insert the styled setup code inside this container element:
    elem.append(markup)
    # Create a title
    h4 = Element('h4')
    h4.text = "Setup code; name= %s" % name
    elem.insert(0, h4)

def code_sample_process(page, elem, uid):
    """Style and saves a copy of the sample code. This code currently
    does not work because it depends on the obsoleted style_pycode
    service in the colourize plugin."""

    raise NotImplementedError()

    vlam = elem.attrib["title"]
    name = extract_name(vlam)
    names[uid] = name
    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("code_test_included") :
            page.add_include("code_test_included")
            page.add_js_code(code_test_jscode)
            page.add_js_code(complete_test_jscode)
            page.add_css_code(css)
            insert_comprehensive_test_button(page)
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
    elem.attrib["id"] = "div_" + uid
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
    return

# javascript code for individual tests
code_test_jscode = u"""
function exec_code_check(uid){
    var j = new XMLHttpRequest();
    j.open("POST", "/check_code?uid="+uid, false);
    j.send('');
};
"""

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
    elem.attrib["id"] = "div_" + uid
    elem.attrib['class'] = "test_output"
    # Create a title
    h4 = SubElement(elem, 'h4')
    h4.text = "Expected output; name= %s" % name
    # a container with the expected output
    pre = SubElement(elem, "pre")
    pre.text = expected_output

def insert_comprehensive_test_button(page):
    '''inserts a button to enable all tests on a page be executed with
       a single click'''
    style = "margin-left: 400px; font-size: 40pt"
    text = "Run all tests"
    action = "check_all_code_samples('%s')" % page.pageid

    label = 'btn1_' + page.pageid
    btn1 = Element("button", style=style, onclick=action, id=label, label=label)
    btn1.text = text
    page.body.insert(0, btn1)  # insert at the top

    label = 'btn2_' + page.pageid
    btn2 = Element("button", style=style, onclick=action, id=label, label=label)
    btn2.text = text
    page.body.append(btn2)  # append at the bottom
    return

# javascript code for all the tests on a page
complete_test_jscode = u"""
function check_all_code_samples(pageid){
    var j = new XMLHttpRequest();
    j.open("POST", "/check_all_code_samples?pageid="+pageid, false);
    j.send('');
};
"""

def run_sample(name):  # tested
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
    # since Crunchy often redefines sys.stdout, we can't simply set
    # it back to sys.__stdout__ after redirection
    saved_stdout = sys.stdout
    redirected = StringIO()
    sys.stdout = redirected
    exec(complete_code)
    sys.stdout = saved_stdout
    return compare(expected_outputs[name], redirected.getvalue())

def compare(s1, s2):  # tested
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
def extract_name(vlam):  # tested
    '''extracts the value of name in a vlam title attribute'''
    # assume vlam is something like "some_keyword junk name=some_name"
    # possibly with some spaces around the equal sign
    result = name_pattern.search(vlam)
    return result.groups()[0]
