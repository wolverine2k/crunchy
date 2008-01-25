'''doc_code_check.py

Plugin designed to perform automatic checks on Python code included in
documentation.  It can handle the case where the Python code has to
be run with some pre-condition, and compares the actual output with
some expected output.'''

import copy
import difflib
import sys

from src.interface import StringIO, plugin, Element, SubElement

code_setups = {}
code_samples = {}
expected_outputs = {}

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
    plugin['register_tag_handler']("pre", "title", "code_setup",
                                          code_setup_process)
    plugin['register_tag_handler']("pre", "title", "code_sample",
                                          code_sample_process)
    plugin['register_tag_handler']("pre", "title", "code_output",
                                          expected_output_process)
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler'](
                         "/code_test%s"%plugin['session_random_id'],
                                       doc_code_check_runner_callback)

def doc_code_check_runner_callback():
    pass

def code_setup_process(page, elem, uid):
    """Style and saves a copy of the setup code"""
    vlam = elem.attrib["title"]

    # next, we style the code, also extracting it in a useful form
    setup_code, markup, error = plugin['services'].style_pycode(page, elem)
    if error is not None:
        markup = copy.deepcopy(elem)
    # which we store
    code_setups[uid] = setup_code
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
    h4.text = "Setup code; name= %s"%vlam.split(' ')[1]
    elem.insert(0, h4)

def code_sample_process(page, elem, uid):
    """Style and saves a copy of the sample code"""
    vlam = elem.attrib["title"]

    # next, we style the code, also extracting it in a useful form
    sample_code, markup, error = plugin['services'].style_pycode(page, elem)
    if error is not None:
        markup = copy.deepcopy(elem)    # which we store
    code_samples[uid] = sample_code
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
    h4.text = "Sample code; name= %s"%vlam.split(' ')[1]
    elem.insert(0, h4)

def expected_output_process(dummy, elem, uid):
    """Displays and saves a copy of the expected output"""
    vlam = elem.attrib["title"]
    expected_output = elem.text
    # which we store
    expected_outputs[uid] = expected_output
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
    h4.text = "Expected output; name= %s"%vlam.split(' ')[1]
    # a container with the expected output
    pre = SubElement(elem, "pre")
    pre.text = expected_output


def run_sample(name):
    '''Given a setup script, as a precursor, executes a code sample
    and compares the output with some expected result.'''
    if name in code_setups:
        complete_code = code_setups[name] + '\n' + code_samples[name]
    else:
        complete_code = code_samples[name]
    saved_stdout = sys.stdout # Crunchy often redefines sys.stdout
    redirected = StringIO()
    sys.stdout = redirected
    exec(complete_code)
    sys.stdout = saved_stdout
    print(compare(expected_outputs[name], redirected.getvalue()))

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