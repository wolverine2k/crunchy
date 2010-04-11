#!/usr/bin/python

# -*- coding: utf-8 -*-
#
import os

# local_browser_root is the base directory from which files can be imported
# via a "local browser widget".  There are a few such widgets, each to
# import a different type of files: html tutorials, Python files, rst files, etc.
#
# The default value will expose only the directory of the person
# who started Crunchy.  This should likely not be used when running
# Crunchy in a server mode, where multiple users could view all the files
# of the process owner.
#
# It is also possible to give a specific base directory.  If the directory
# does not exists, the entire directory structure will be accessible
# subject to the permission of the person who started Crunchy.
# Note that Windows users should probably use forward slashes "/" instead
# of backslashes "\" in path (or used raw strings, or make sure they escape
# backslashes properly...)

local_browser_root = os.path.expanduser("~")  # comment out if you wish :-)

#local_browser_root = "/Users/andre"     # a random example as alternative :-)
#local_browser_root = "does_not_exist"   # for testing purposes


