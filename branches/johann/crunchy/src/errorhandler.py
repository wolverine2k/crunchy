'''
errorhandler.py

Handle errors produced while running Crunchy Frog, displaying the result to 
the user in a friendly way.
At present, this is just a very basic module.  Translations to languages other
than English and fancier error processing will eventually take place here.
'''

# The basic javascript code used displays an alert window to the user and
# goes back to the last page which did not have an error.
#
#This code could be "improved" by doing a custom "Crunchy Frog" alert, perhaps
# using something like the code on http://slayeroffice.com/code/custom_alert/

from translation import _

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

class ColourNameError(CrunchyError):
    '''Used for invalid colour specification in canvas'''
    def __init__(self, colour):
        self.colour = colour
    def __str__(self):
        return str(self.colour)

class NoSoundError(CrunchyError):
    '''Used for invalid trying to use sound when module is not present'''
    def __init__(self, info):
        self.msg = info
    def __str__(self):
        return str(self.msg)

class PythonExecutionError(CrunchyError):
    '''Used for handling general error from execution of user-code.'''
    def __init__(self, info):
        self.info = info
    def __str__(self):
        return str(self.info)

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

def IOError_error_dialog(info):
    return begin_javascript_alert + str(info) + end_javascript_alert

def colour_name_dialog(colour):
    return _("Canvas error: %s is an invalid colour.")%colour

def canvas_error_dialog(info):
    return _("Canvas error.  Python info: %s.")%info

def python_error_dialog(info):
    '''General error dialog.  Sprinkle throughout.'''
    return _("Python execution error.  Info: %s.")%info

def parsing_error_dialog(info):
    '''Information given when the code colourizer fails.'''
    return _("Parsing error occurred in the following Python code.\nInfo: %s.")%info

###================
# The following are "unexpected" errors.  Typically, they are errors which
# have never occurred, or not occurred since some bugs have been fixed,
# or error of a different type than those that are expected to occur.
# They are included as diagnostic tools "just in case".

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

def unexpected_Tutorials_get_error_dialog(args):
    msg=_("Unrecognized argument in Tutorials.get(): %s. ")%args +\
        _("This should never happen - and has not happened since the last bug fix!")+\
        _(" Please contact the developpers with a copy of the html file ")+\
        _("that caused this problem, and a description of what was done.")
    return javascript_alert%msg
