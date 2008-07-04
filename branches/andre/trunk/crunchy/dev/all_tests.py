# -*- coding: utf-8 -*-
'''
all_tests.py

Runs a series of tests contained in text files, using the doctest framework.
All the tests are asssumed to be located in the "src/tests" sub-directory.
'''

from doctest import OutputChecker
original_check_output = OutputChecker.check_output
import doctest
import os
import sys

# sometime we want to ignore Crunchy's output as it may be in a
# unpredictable language, based on user's preferences.

# define a new doctest directive to ignore the output of a given test

IGNORE_OUTPUT = doctest.register_optionflag("IGNORE_OUTPUT")

class MyOutputChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if optionflags & IGNORE_OUTPUT:
            return True
        return original_check_output(self, want, got, optionflags)

doctest.OutputChecker = MyOutputChecker
# end of new directive definition and replacement (monkeypatching)

os.chdir("..")
sys.path.insert(0, os.getcwd())
test_path = os.path.join(os.getcwd(), "src", "tests")
test_files = [f for f in os.listdir(test_path) if f.startswith("test_")
              and f.endswith(".rst")]

sep = os.path.sep

nb_files = 0

#TODO: add a command line option to replace this
excluded = []#["test_colourize.rst"]

#TODO: add a command line option to replace this
include_only = ['test_configuration.rst']

#TODO: add a command line option (clean?) that would remove all .pyc
# files before testing.
#TODO: add a command line option that would remove the current .crunchy
# directory to start unit tests from the point of view of a new user.

for t in test_files:
    if t in excluded:
        continue # skip
    #if t not in include_only:
    #    continue
    failure, nb_tests = doctest.testfile("src" + sep + "tests" + sep + t)
    print "%d failures in %d tests in file: %s"%(failure, nb_tests, t)
    nb_files += 1

print "number of test files run: ", nb_files

# Note that the number of tests, as identified by the doctest module
# is equal to the number of commands entered at the interpreter
# prompt; so this number is normally much higher than the number
# of test.
