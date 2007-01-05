'''
errors.py

Handle errors produced while running Chewy.
'''

import sys
import traceback
from StringIO import StringIO

from translation import _


# The basic javascript code used displays an alert window to the user and
# goes back to the last page which did not have an error.
#
#This code could be "improved" by doing a custom "chewy" alert, perhaps
# using something like the code on http://slayeroffice.com/code/custom_alert/

## Note: because css files often contain "%", we can't use them to build
# a string that will then be formatted with " %s ..."%param
# as the "%" in the css file will cause an error. This is why we
# use a simple concatenation to build the error message string in
# HTMLTreeBuilder_error_dialog and IOError_error_dialog.

css = open('src/css/custom_alert.css').read()
js = open('src/javascript/custom_alert.js').read()
begin_javascript_alert = '''
<html>
<head>
<title></title>
<style>%s</style>
<script type='text/javascript'>
%s
function normalAlert(){  // redefining it
removeCustomAlert();
history.go(-1);return false;}
function init(){
window.alert(\"'''%(css, js)

end_javascript_alert='''\");
}
</script>
</head>
<body onload="init();">
</body>
</html>
'''

###------------------
# Note:  The string passed to the javascript alert can not contain newlines.
###------------------

class CrunchyError(Exception):
    '''General class to derive exceptions from.'''
    pass


class HTMLTreeBuilderError(CrunchyError):
    '''Used for handling parsing errors by elementtree.'''
    def __init__(self, path, info):
        self.info = info
        self.path = path.replace("\\", '/')
    def __str__(self):
        return _("Error in processing %s: %s") %(self.path, self.info)

def HTMLTreeBuilder_error_dialog(e):
    mesg = _("The file '%s' has some html errors in it: %s.")%(e.path,
              e.info) + _("  It can not be displayed.")
    return begin_javascript_alert + mesg + end_javascript_alert

###================
# The following are "unexpected" errors.  Typically, they are errors which
# have never occurred, or not occurred since some bugs have been fixed,
# or error of a different type than those that are expected to occur.
# They are included as diagnostic tools "just in case".

def IOError_error_dialog(info):
    return begin_javascript_alert + str(info) + end_javascript_alert

def unexpected_file_error_dialog(function, filename, info):
    msg = _("Unexpected error in %s. ")%function +\
            _("This occurred while trying to open %s. ")%filename +\
            _("The information given by Python is: %s.")%info
    return javascript_alert%msg

def unexpected_KeyError_error_dialog(function, filename, TREES, info):
    msg = _("Unexpected error in %s. ")%function +\
        _("This occurred while trying to process the tree for %s. ")%filename +\
        _("The files processed so far are %s. ")%TREES +\
        _("The information given by Python is: %s.")%info
    return javascript_alert%msg





