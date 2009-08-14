"""  Crunchy pyflakes plugin.

This plugin is an analyzer backend for pyflakes.
"""

import sys

pyflakes_available = False
try:
    import compiler      # not found in Python 3.1
    from pyflakes import checker
    pyflakes_available = True
except ImportError:
    pass

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, StringIO

# The set of other "widgets/services" required from other plugins
requires =  set(["analyzer_widget"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register one 'action':
       the get_analyzer_pyflakes service, that return a object to
       analyze the code.
       """
    if pyflakes_available:
        # Register the analyzer
        # Important: the vlam_option is the identifier of the analyzer.
        # The same identifiant must be used for the service: get_analyzer_id
        plugin['add_vlam_option']('analyzer', 'pyflakes')
        plugin['register_service'](
            'get_analyzer_pyflakes',
            CrunchyFlakes(),
        )
        plugin['services'].register_analyzer_name('pyflakes')#, 'PyFlakes')

class CrunchyFlakes:
    """Class to configure and start a pyflakes analysis
    """

    def __init__(self):
        self._report = None
        self._code = None
        self._nb_errors = None

    #def set_code(self, code):
    #    """Set the code to analyze"""
    #    self._code = code

    def run(self, code):
        """Make the analysis

        This function is inspired from the check function of the pyflakes start
        script.
        """
        print("run called in pychecker")
        self._code = code
        # Open a buffer for the output
        output = StringIO()
        # Start the check
        try:
            tree = compiler.parse(self._code)
        except (SyntaxError, IndentationError):
            value = sys.exc_info()[1]
            try:
                (lineno, offset, line) = value[1][1:]
            except IndexError:
                print >> output, _('Could not compile the code.')
            else :
                if line.endswith("\n"):
                    line = line[:-1]
                print >> output, _('line %d: could not compile') % lineno
                print >> output, line
                print >> output, " " * (offset-2), "^"
            self._nb_errors = None
        else:
            w = checker.Checker(tree, 'line')
            w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
            for warning in w.messages:
                print >> output, warning
            self._nb_errors = len(w.messages)

        # Get the output and remove the irrelevant file path
        self._report = output.getvalue()
        # Close the buffer
        output.close()

    def get_report(self):
        """Return the full report"""
        return "Report from pyflakes\n" + self._report

    def get_global_score(self):
        """Return the global score or None if not available.

        This score can be formatted with "%.2f/10" % score

        It is not computed by pychecker, but here, by the formule:
        score = 10 - ((number_of_errors / number_of_lines) * 10)
        """
        if self._nb_errors is None:
            return None
        # Just count non-empty and non-comment lines
        code_lines = [line for line in self._code.split('\n') \
                      if line.strip() and not line.strip().startswith('#')]
        number_of_lines = float(len(code_lines))
        number_of_errors = float(self._nb_errors)
        return 10 - ((number_of_errors / number_of_lines) * 10)

    def _printWarnings(self, warnings, stream=None):
        """This function call the original checker._printWarnings, but set
        the stream to self._output_buffer
        """
        original_printWarnings(warnings, self._output_buffer)
