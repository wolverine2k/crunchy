'''
Intended to provide an interface to the cluetip jquery plugin.

Inserts the required html and javascript content to include cluetips.
'''

from crunchy.interface import plugin
from crunchy.security import specific_allowed

def register():
    '''registers tag handlers for popup helpers'''
    for tag in specific_allowed:
        plugin['register_tag_handler'](tag, "title", "cluetip", insert_cluetip)
    plugin['register_service']("insert_cluetip", insert_cluetip)

def insert_cluetip(page, elem, uid):
    '''inserts the required javascript to insert cluetips'''

    if not page.includes("jquery.dimensions.js"):
        page.add_include("jquery.dimensions.js")
        page.insert_js_file("/javascript/jquery.dimensions.js")

    if not page.includes("jquery.cluetip.js"):
        page.add_include("jquery.cluetip.js")
        page.insert_js_file("/javascript/jquery.cluetip.js")

    if not page.includes("jquery.hoverIntent.js"):
        page.add_include("jquery.hoverIntent.js")
        page.insert_js_file("/javascript/jquery.hoverIntent.js")
        page.insert_css_file("/css/jquery.cluetip.css")

    elem.attrib['title'] = elem.attrib['title'][7:] # remove keyword "cluetip"
    uid = "cluetip_%s" % uid
    if 'class' in elem.attrib:
        elem.attrib['class'] += ' %s' % uid
    else:
        elem.attrib['class'] = uid
    if 'rel' in elem.attrib:
        if ' ' not in elem.attrib['rel']:
            # pull a single page using ajax...
            page.add_js_code(js_code_rel % (elem.tag, uid))
        else:
            # pull multiple pages using ajax...
            paths = elem.attrib['rel'].split(' ')
            args = ""
            for path in paths:
                if path: # multiple spaces will result in null strings
                    args += "'%s', " % path
            args = args[:-2] # removed trailing comma
            page.add_js_code(js_code_multiple % (uid, elem.tag, uid, uid, args))
    else:
        # use info from title element
        page.add_js_code(js_code_title % (elem.tag, uid))

js_code_rel = """
$(document).ready(function() {
  $('%s.%s').cluetip({width: 600, sticky: true, activation: 'click'});
});"""

js_code_title = """
$(document).ready(function() {
  $('%s.%s').cluetip({
  splitTitle: '|',
  width: '300px;',
  sticky: true,
  activation: 'click'
  });
});
"""

js_code_multiple = """
    $(document).ready(function() {

      function multipleFiles%s() {
        var contents = '';
        var index=0;
        // can't use "<" as it will be transformed into "&lt;"
        for (var i=0, arglength=arguments.length; i != arglength; i++) {

          $.ajax({
            url: arguments[i],
            success: function(txt) {
              contents += txt;
              if (index == arglength-1) {
                $('%s.%s').cluetip(contents, {width: '600px' , height: '450px',
                                              sticky: true, dropShadow: false,
                                              activation: 'click'
                                              });
              }
              index++;
            }
          });
        }
      }
      multipleFiles%s(%s);
    });
"""
