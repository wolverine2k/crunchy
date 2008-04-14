#!/usr/bin/env python
# encoding: utf-8
"""
build_release.py

Created by Johannes Woolard on 2008-04-14.
"""

import sys
from subprocess import call

import pysvn

help_message = '''build_release.py
Usage: python build_release 'version'

Run this from an empty directory - it will download the appropriate release version from
http://crunchy.googlecode.com/svn/tags/'version' (where version is the version given as
an argument to te command).

IMPORTANT: Always run this from an empty directory.

Final release files will end up in the curent working directory. Temporary files will be downloaded to ./tmp

This script relies on pysvn from http://pysvn.tigris.org/
'''


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 2:
        sys.stderr.write(help_message)
        return 2
    version = argv[1]
    print "Creating dist packages for Crunchy, version %s" % version
    
    print "Exporting dist from http://crunchy.googlecode.com/svn/tags/%s" % version
    client = pysvn.Client()
    revision = client.export("http://crunchy.googlecode.com/svn/tags/%s" % version, "./crunchy-%s"%version)
    print "Successfully exported revision %s from http://crunchy.googlecode.com/svn/tags/%s" % (revision.number, version)
    
    create_zip(version)
    
    return 0

def create_zip(version):
    print "Creating crunchy-%s.zip" % version
    retcode = call(["/usr/bin/zip", "-q", "-r", "crunchy-%s.zip" % version, "crunchy-%s" % version])
    if retcode == 0:
        print "zip file succesfully created"
    else:
        raise "zip returned error code %s" % retcode

if __name__ == "__main__":
    sys.exit(main())
