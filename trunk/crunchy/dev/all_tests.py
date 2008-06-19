# -*- coding: utf-8 -*-
'''
all_tests.py

Runs a series of tests contained in text files, using the doctest framework.
All the tests are asssumed to be located in the "src/tests" sub-directory.
'''

import doctest
import os
import sys

os.chdir("..")
sys.path.insert(0, os.getcwd())
test_path = os.path.join(os.getcwd(), "src", "tests")
test_files = [f for f in os.listdir(test_path) if f.startswith("test_")]

sep = os.path.sep

nb_files = 0
excluded = []#["test_colourize.rst"]

#include_only = ['test_handle_remote.rst']
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
