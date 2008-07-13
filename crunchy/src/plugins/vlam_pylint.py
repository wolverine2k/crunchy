"""  Crunchy pylint plugin.

This plugin is an analyzer backend for pylint.
"""

import os
import StringIO
import tempfile
try:
    from pylint import lint, checkers
    from pylint.checkers.base import BasicChecker
    pylint_available = True
except ImportError:
    pylint_available = False

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin

# The set of other "widgets/services" required from other plugins
requires =  set()

if pylint_available:
    # We redefine the verification of docstring
    old_check_docstring = BasicChecker._check_docstring
    def replaced_check_docstring(self, node_type, node):
        """Check the node has a non empty docstring
        
        This modified method prevent to raise a message for a module missing
        docstring.
        """
        if node_type != 'module':
            old_check_docstring(self, node_type, node)
    BasicChecker._check_docstring = replaced_check_docstring

class CrunchyLinter:
    """Class to configure and start a pylint analyze
    
    Based on the Run class from pylint.lint
    """
    
    def __init__(self, reporter=None, quiet=0, pylintrc=None):
        self.LinterClass = lint.PyLinter
        self._rcfile = pylintrc
        self.linter = self.LinterClass(
            reporter=reporter,
            pylintrc=self._rcfile,
        )
        self.linter.quiet = quiet
        self._report = None
        self._code = None
        # register standard checkers
        checkers.initialize(self.linter)
        # read configuration
        self.linter.read_config_file()
        self.linter.load_config_file()
        # Disable some errors.
        self.linter.load_command_line_configuration([
            '--module-rgx=.*',  # don't check the module name
            '--reports=n',      # remove tables
            '--persistent=n',   # don't save the old score (no sens for temp)
        ])
        self.linter.load_configuration()
        self.linter.disable_message('C0121')# required attribute "__revision__"
        if reporter:
            self.linter.set_reporter(reporter)
    
    def set_code(self, code):
        """Set the code to analyze"""
        self._code = code
    
    def run(self):
        """Make the analysis"""
        # Save the code in a temporary file
        tempfile.tempdir = config['temp_dir']
        temp = tempfile.NamedTemporaryFile(suffix = '.py')
        temp.write(self._code)
        temp.flush()
        # Open a buffer for the output
        output_buffer = StringIO.StringIO()
        self.linter.reporter.set_output(output_buffer)
        # Start the check
        self.linter.check(temp.name)
        # Get the output and remove the irrelevant file name
        self._report = output_buffer.getvalue().replace(
                            os.path.splitext(os.path.basename(temp.name))[0],
                            'line ')
        # Close files
        output_buffer.close()
        temp.close()
    
    def get_report(self):
        """Return the full report"""
        return self._report
    
    def get_global_score(self):
        """Return the global score or None if not available.
        
        This score can be formatted with "%.2f/10" % score
        """
        # Make sure there is a global_note (if --report=n, the global_note
        # is not calculated)
        if not 'global_note' in self.linter.stats:
            self.linter.report_evaluation([], self.linter.stats, {})
        return self.linter.stats['global_note']

def register():
    """The register() function is required for all plugins.
       In this case, we need to register one 'action':
       the get_analyzer service, that return a object to analyze the code.
       """
    if pylint_available:
        # Register the analyzer
        # TODO: only if pylint is the default analyzer in the configuration
        plugin['register_service']('get_analyzer', (lambda : CrunchyLinter()))
