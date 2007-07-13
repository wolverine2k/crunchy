'''
all_tests.py

Runs a series of tests contained in text files, using the doctest framework.
All the tests are asssumed to be located in the "src/tests" sub-directory.
'''

import doctest
import os.path

test_files = [ "test_colourize.txt",
              "test_pluginloader.txt",
              "test_file_service.txt",
              "test_configuration.txt",
              "test_utilities.txt" ]

for t in test_files:
   failure, nb_tests = doctest.testfile("src" + os.path.sep +
                                        "tests" + os.path.sep + t)
   print "%d failures in %d tests in file: %s"%(failure, nb_tests, t)

print """========
   Sometimes, the first test will fail due to importing configuration.py
which prints out some diagnostic that should be ignored."""

# Note that the number of tests, as identified by the doctest module
# is equal to the number of commands entered at the interpreter
# prompt; so this number is normally much higher than the number
# of test.

