#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
all_tests.py

Runs a series of tests contained in text files, using the doctest framework.
All the tests are asssumed to be located in the current directory, referencing
files in the parent directory.
'''

from doctest import OutputChecker
original_check_output = OutputChecker.check_output
import doctest
import os
import random
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
cwd = os.getcwd()
sys.path.insert(0, cwd)
test_path = os.path.join(os.getcwd(), "tests")
test_files = [f for f in os.listdir(test_path) if f.startswith("test_")
              and f.endswith(".rst")]

# do the test in somewhat arbitrary order in order to try and
# ensure true independence.
random.shuffle(test_files)

sep = os.path.sep

nb_files = 0
total_tests = 0
total_failures = 0
files_with_failures = 0
all_files_with_failures = []

#TODO: add a command line option to replace this
include_only = []

#TODO: add a command line option to replace this
excluded = []#["test_colourize.rst"] # now obsolete

#TODO: add a command line option (clean?) that would remove all .pyc
# files before testing.
#TODO: add a command line option that would remove the current .crunchy
# directory to start unit tests from the point of view of a new user.


for t in test_files:
    if t in excluded:
        continue # skip
    if include_only:
        if t not in include_only:
            continue
    failure, nb_tests = doctest.testfile(os.path.join("tests", t))
    total_tests += nb_tests
    total_failures += failure
    if failure > 0:
        files_with_failures += 1
        all_files_with_failures.append((failure, t))
    print "%d failures in %d tests in file: %s"%(failure, nb_tests, t)
    nb_files += 1

print "-"*50
print "%d failures in %d tests in %s files out of %s." % (total_failures,
                                total_tests, files_with_failures, nb_files)
for info in all_files_with_failures:
    print "%3d failures in %s" % (info)

# Note that the number of tests, as identified by the doctest module
# is equal to the number of commands entered at the interpreter
# prompt; so this number is normally much higher than the number
# of test.
