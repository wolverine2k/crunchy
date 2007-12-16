'''
all_tests_py3k.py

Runs a series of tests contained in text files, using the doctest framework.
All the tests are asssumed to be located in the "src/tests" sub-directory.

This file is running under Python 3+
'''

import doctest
from os import listdir, getcwd
from os.path import join, sep, dirname
from imp import find_module

test_path = join(dirname(find_module("crunchy")[1]), "src", "tests")
test_files = [f for f in listdir(test_path) if f.startswith("test_")]

#excluded = ['test_colourize.txt']#, 'test_configuration.txt']
target =['test_universal.txt', 'test_utilities.txt']
for t in test_files:
    if t not in target:
        continue
    failure, nb_tests = doctest.testfile("src" + sep + "tests" + sep + t)
    print ("{0} failures in {1} tests in file: {2}".format(failure, nb_tests, t))
    if failure:
        break

#print("""\n========
#
#Sometimes, the test_configuration will fail due to importing configuration.py
#which prints out some diagnostic that should be ignored.""")

# Note that the number of tests, as identified by the doctest module
# is equal to the number of commands entered at the interpreter
# prompt; so this number is normally much higher than the number
# of test.
