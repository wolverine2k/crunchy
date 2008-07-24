"""  Crunchy pychecker plugin.

This plugin is an analyzer backend for pychecker.
"""

import os
import StringIO
import tempfile
try:
    # Try to import pychecker, but without checking the Crunchy code
    os.environ['PYCHECKER_DISABLED'] = '1'
    from pychecker import checker
    os.environ['PYCHECKER_DISABLED'] = '0'
    pychecker_available = True
except ImportError:
    pychecker_available = False

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin

# The set of other "widgets/services" required from other plugins
requires =  set()

def register():
    """The register() function is required for all plugins.
       In this case, we need to register one 'action':
       the get_analyzer_pychecker service, that return a object to
       analyze the code.
       """
    if pychecker_available:
        # Register the analyzer
        # Important: the vlam_option is the identifier of the analyzer.
        # The same identifiant must be used for the service: get_analyzer_id
        plugin['add_vlam_option']('analyzer', 'pychecker') 
        plugin['register_service'](
            'get_analyzer_pychecker',
            CrunchyChecker(),
        )

# Keep the original checker._printWarnings
original_printWarnings = checker._printWarnings

class CrunchyChecker:
    """Class to configure and start a pychecker analysis
    """
    
    def __init__(self):
        self._report = None
        self._code = None
        self._output_buffer = None
    
    def set_code(self, code):
        """Set the code to analyze"""
        self._code = code
    
    def run(self):
        """Make the analysis"""
        # Save the code in a temporary file
        temp = tempfile.NamedTemporaryFile(suffix = '.py')
        temp.write(self._code)
        temp.flush()
        # Open a buffer for the output, and change the pychecker.printer
        # function to write inside.
        self._output_buffer = StringIO.StringIO()
        checker._printWarnings = self._printWarnings
        # Start the check
        checker.main(['dummy_arg', '--only', temp.name])
        # Get the output and remove the irrelevant file path
        self._report = self._output_buffer.getvalue().replace(temp.name,
                                                              'line')
        # Close files
        self._output_buffer.close()
        temp.close()
    
    def get_report(self):
        """Return the full report"""
        return self._report
    
    def get_global_score(self):
        """Return the global score or None if not available.
        
        This score can be formatted with "%.2f/10" % score
        
        It is not computed by pychecker, but here, by the formule:
        score = 10 - ((number_of_errors / number_of_lines) * 10)
        """
        if not "UNABLE TO IMPORT" in self.get_report():
            # Just count non-empty and non-comment lines
            code_lines = [line for line in self._code.split('\n') \
                          if line.strip() and not line.strip().startswith('#')]
            report_lines = [line for line in self.get_report().split('\n') \
                            if line]
            number_of_errors = float(len(report_lines))
            number_of_lines = float(len(code_lines))
            return 10 - ((number_of_errors / number_of_lines) * 10)
        else:
            return None
    
    def _printWarnings(self, warnings, stream=None):
        """This function call the original checker._printWarnings, but set
        the stream to self._output_buffer
        """
        original_printWarnings(warnings, self._output_buffer)
