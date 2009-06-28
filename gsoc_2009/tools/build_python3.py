#!/usr/bin/env python

import os
import os.path as paths
import shutil
import sys
from pprint import pformat
from subprocess import call

# Help message printed to STDERR when requested in main().
HELP = """build_python3.py
Usage:

* python[3.x] build_python3.py {filename} {dest}
  Copies the file from filename to dest and runs the 2to3 tool on
  the destination.
"""

# Arguments for subprocess.call() below.
rsync = ['rsync',
         '-avz',
         '--delete',
         '--exclude=.svn/',
         '--exclude=pygments/',
         '--exclude=*.pyc',
         ]

_2TO3 = ['2to3', '-w']

class Error(SystemExit):
    """A SystemExit with error strings included."""

    _2to3 = \
        'Called 2to3 with \n{args}\nand it exited with {ret}'

    def __init__(key, **kw):
        """Prints a specified error to standard error then constructs
        a SystemExit instance with status code 1."""

        text = getattr(Error, key).format(**kw)
        sys.stderr.write('build_python3.py: error: {}\n'.format(text))
        # Status code is always one.
        super().__init__(1)

def copy(src, dst):
    """Copies file at src to path at dst and logs it to stdout."""

    print('Copying {} to {}'.format(src, dst))
    shutil.copyfile(src, dst)

def main_copy(src, dst):
    """Copies src to dst and then runs the mutating 2to3 on dst in a
    subprocess."""

    copy(src, dst)

    # Call 2to3.
    args = _2TO3 + [dst]
    ret  = call(args)
    if not ret == 0:
        raise Error('_2to3', args=args, ret=ret)

    raise SystemExit()

def main():
    """Parses command-line arguments and raises the appropriate
    SystemExit exception."""

    argv = sys.argv
    if '--help' in argv or '-h' in argv:
        sys.stderr.write(HELP)
        raise SystemExit(2)

    # Not enough arguments passed for {filename} and {dest}
    if len(sys.argv) < 3:
        sys.stderr.write(HELP)
        raise SystemExit(1)

    main_copy(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
