#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
all_tests.py

Runs a series of tests contained in text files, using the doctest framework.
All the tests are asssumed to be located in the "src/tests" sub-directory.

This should be run from the base directory (crunchy).
'''

#TODO ??: add a command line option (clean?) that would remove all .pyc
# files before testing.
#TODO ??: add a command line option that would remove the current .crunchy
# directory to start unit tests from the point of view of a new user.

# Note for self: using with coverage:
# python dev/all_tests.py --nose
# coverage -b -d cover -i -m
# then look for index.html inside cover directory

import doctest
import os
import random
import sys
from doctest import OutputChecker
from os.path import realpath
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--det", dest="det",
                  action="store_true",
                  help="Run the tests deterministically (in alphabetical order)")

parser.add_option("-i", "--include_only", dest="incl",
                  action="append", type="string",
                  help="Test only this file; can be passed multiple times for multiple files"\
                       " (file extension '.rst' and prefix 'test_' optional)")

parser.add_option("-x", "--exclude", dest="excl",
                  action="store", type="string",
                  help="Exclude this file; can be passed multiple times for multiple files"\
                       "; ignored if --include_only is present" \
                       " (file extension '.rst' and prefix 'test_' optional)")

parser.add_option("--nose", dest="nose",
                  action="store_true",
                  help="Turns into a thin wrapper over nosetests")

options, args = parser.parse_args()

# Sometime we want to ignore Crunchy's output as it may be in a
# unpredictable language, based on user's preferences.
#
# Define a new doctest directive to ignore the output of a given test
# and monkeypatch OutputChecker with it.
original_check_output = OutputChecker.check_output
IGNORE_OUTPUT = doctest.register_optionflag("IGNORE_OUTPUT")
class MyOutputChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if optionflags & IGNORE_OUTPUT:
            return True
        return original_check_output(self, want, got, optionflags)

doctest.OutputChecker = MyOutputChecker

test_path = realpath(os.path.dirname(__file__))
test_path = realpath(os.path.join(test_path, '../src/tests'))
sys.path.insert(0, realpath(os.path.join(test_path, '../..')))

# Turn into nosetests if asked.
if options.nose:
    from nose.core import run
    argv = ['-w', test_path,
            #'--verbose',
            '--exclude=how_to.rst',
            '--with-doctest',
            '--doctest-extension=.rst',
            '--with-coverage',
            #'--cover-html',
            '--cover-inclusive',
            '--with-isolation'
            ]
    run(argv=argv)
    raise SystemExit()

test_file_names = [f for f in os.listdir(test_path)
              if f.startswith("test_") and f.endswith(".rst")]

def normalize_name(filename):
    '''ensures that a test file name is of the form test_X.rst'''
    if not filename.endswith(".rst"):
        filename += ".rst"
    if not filename.startswith("test_"):
        filename = "test_" + filename
    return filename

if options.incl:
    included_files = []
    for f in options.incl:
        f = normalize_name(f)
        if f in test_file_names:
            included_files.append(f)
    if not included_files:
        print("No such file has been found.")
        print(test_file_names)
        sys.exit()
    else:
        test_file_names = included_files
elif options.excl:
    excluded_files = False
    for f in options.excl:
        f = normalize_name(f)
        if f in test_file_names:
            test_file_names.remove(f)
            excluded_files = True
        else:
            print("WARNING: %s is not a known test file" % f)

test_files = [os.path.join(test_path, f) for f in test_file_names]

if not options.det:
    # do the test in somewhat arbitrary order in order to try and
    # ensure true independence.
    random.shuffle(test_files)

sep = os.path.sep

nb_files = 0
total_tests = 0
total_failures = 0
files_with_failures = 0
all_files_with_failures = []

for t in test_files:
    failure, nb_tests = doctest.testfile(t, module_relative=False)
    total_tests += nb_tests
    total_failures += failure
    if failure > 0:
        files_with_failures += 1
        all_files_with_failures.append((failure, t))

    print("%d failures in %d tests in file: %s"%(failure, nb_tests, t))
    nb_files += 1

print("-"*50)
print("%d failures in %d tests in %s files out of %s." % (total_failures,
                                total_tests, files_with_failures, nb_files))
for info in all_files_with_failures:
    print("%3d failures in %s" % (info))

# Note that the number of tests, as identified by the doctest module
# is equal to the number of commands entered at the interpreter
# prompt; so this number is normally much higher than the number
# of test.
