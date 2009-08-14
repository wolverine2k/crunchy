"""  Crunchy pylint plugin.

This plugin is an analyzer backend for pylint.
"""

import os
import tempfile
try:
    from pylint import lint, checkers
    from pylint.checkers.base import BasicChecker
    from pylint.reporters import EmptyReport
    pylint_available = True
except ImportError:
    pylint_available = False

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, StringIO

# The set of other "widgets/services" required from other plugins
requires =  set(["analyzer_widget"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register one 'action':
       the get_analyzer_pylint service, that return a object to analyze the
       code.
       """
    if pylint_available:
        # Register the analyzer
        # Important: the vlam_option is the identifier of the analyzer.
        # The same identifiant must be used for the service: get_analyzer_id
        plugin['add_vlam_option']('analyzer', 'pylint')
        plugin['register_service'](
            'get_analyzer_pylint',
            CrunchyLinter(),
        )
        plugin['services'].register_analyzer_name('pylint')
        plugin['add_vlam_option']('analyzer', 'pylint_full')
        plugin['register_service'](
            'get_analyzer_pylint_full',
            CrunchyLinter(crunchy_report="full"),
        )
        plugin['services'].register_analyzer_name('pylint_full')

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
    """Class to configure and start a pylint analysis

    Based on the Run class from pylint.lint
    """
    def __init__(self, reporter=None, quiet=0, pylintrc=None, crunchy_report=None):
        if crunchy_report == "full":
            self.full_report = True
        else:
            self.full_report = False
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
        if self.full_report:
            self.linter.load_command_line_configuration([
                '--module-rgx=.*',  # don't check the module name
                '--persistent=n',   # don't save the old score (no sens for temp)
            ])
        else:
            self.linter.load_command_line_configuration([
                '--module-rgx=.*',  # don't check the module name
                '--reports=n',      # remove tables
                '--persistent=n',   # don't save the old score (no sens for temp)
            ])
        self.linter.load_configuration()
        self.linter.disable_message('C0121')# required attribute "__revision__"
        if reporter:
            self.linter.set_reporter(reporter)

    def run(self, code):
        """Make the analysis"""
        temp = tempfile.NamedTemporaryFile(suffix = '.py')
        temp.write(code)
        temp.flush()

        output_buffer = StringIO()
        self.linter.reporter.set_output(output_buffer)
        self.linter.check(temp.name)
        self._report = output_buffer.getvalue().replace(temp.name, 'line ')

        output_buffer.close()
        temp.close()


    def get_report(self):
        """Return the full report"""
        if self.full_report:
            return "Full report from pylint\n" + self._report
        return "Report from pylint\n" + self._report

    def get_global_score(self):
        """Return the global score or None if not available.

        This score can be formatted with "%.2f/10" % score
        """

        if not 'global_note' in self.linter.stats:
            try:
                self.linter.report_evaluation([], self.linter.stats, {})
            except EmptyReport:
                # If there is no code to make a score
                return None
        return  self.linter.stats['global_note']
