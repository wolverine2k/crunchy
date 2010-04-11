
import filecmp
import os
import os.path as paths
import shutil
import sys
from pprint import pformat
from subprocess import call

# Help message printed to STDERR when requested in main().
HELP = """\
NAME
build_python3.py

USAGE
* python[3.x] build_python3.py {src filename} {dst filename}
  Copies the file from filename to dest and runs the 2to3 tool on
  the destination.

* python[3.x] build_python3.py {src dir} {dst dir}
  Copies all files from the source directory to the destination
  directory and runs 2to3 on those files. Will skip files whose .bak
  counterparts in the destination directory match exactly.
"""

# Argument for subprocess.call().
_2TO3 = ['/usr/local/py3.1/bin/2to3', '-w']

class Error(SystemExit):
    """A SystemExit with error strings included."""

    _2to3 = \
        'Called 2to3 with {args} and it exited with {ret}'

    mismatch = \
        'Both arguments have to be directories, or both have to be files'

    def __init__(self, key, **kw):
        """Prints a specified error to standard error then constructs
        a SystemExit instance with status code 1."""

        text = getattr(Error, key).format(**kw)
        sys.stderr.write('build_python3.py: error: {}\n'.format(text))
        # Status code is always one.
        super().__init__(1)

def copy(src, dst):
    """Copies file at src to path at dst and logs it to stdout. Will
    make the dst directory if necessary."""

    # normpath calling is a must. makedirs does not like os.pardir
    # ('..') in paths.
    dirname = paths.normpath(paths.dirname(dst))
    if not paths.exists(dirname):
        print('Making {}'.format(dirname))
        os.makedirs(dirname)

    print('Copying {} to {}'.format(src, dst))
    shutil.copyfile(src, dst)

def remove(victim):
    """Removes file and logs it to stdout."""

    print('Removing {}'.format(victim))
    os.remove(victim)

def main_copy(src, dst, opts=[]):
    """Copies src to dst and then runs the mutating 2to3 on dst in a
    subprocess. Raises an Error if 2to3 fails."""

    copy(src, dst)

    # Call 2to3.
    args = _2TO3 + opts + [dst]
    ret  = call(args)
    if not ret == 0:
        raise Error('_2to3', args=args, ret=ret)

def parallel_walk(src, dst):
    """Walks both directories. Yields the paths of files in the source
    directory and the expected corresponding path in the
    destination."""
    for root, dirs, files in os.walk(src):
        if '.svn' in dirs:
            dirs.remove('.svn')

        for file in files:
            a = paths.join(root, file)
            b = a.replace(src, dst, 1)
            yield a, b

def main_deep_copy(src, dst):
    """Walks the src directory and copies each file to dst before
    running 2to3 on it. Skips unnecessary files. Raises an Error if
    2to3 fails."""

    for a, b in parallel_walk(src, dst):
        root, ext = paths.splitext(a)

        if ext == '.pyc':
            # Unnecessary, but just to be sure: Clean up .pyc files in
            # case it conflicts with newer .py files.
            if paths.exists(b):
                os.remove(b)

        elif ext in ('.py', '.rst'):
            # os.path.join thinks "b" is a directory and does the
            # wrong thing here.
            bak = b + '.bak'

            if paths.exists(b):
                # Skip if .bak exists and is a match, indicating the
                # source file has not changed.
                if paths.exists(bak):
                    if filecmp.cmp(a, bak):
                        print('Skipping {}: unchanged'.format(a))
                        continue

                # If no .bak file exists, that means 2to3 skipped the
                # file.
                else:
                    if filecmp.cmp(a, b):
                        print('Skipping {}: unchanged'.format(a))
                        continue

            if ext == '.py':
                main_copy(a, b)
            else:
                main_copy(a, b, opts=['-d'])

        else:
            if not paths.exists(b) or not filecmp.cmp(a, b):
                copy(a, b)

def main():
    """Parses command-line arguments and raises the appropriate
    SystemExit exception."""

    argv = sys.argv
    if '--help' in argv or '-h' in argv:
        sys.stderr.write(HELP)
        raise SystemExit(2)

    # {filename} and {dest} were passed.
    if len(sys.argv) == 3:
        src, dst = sys.argv[1:3]
        if paths.isdir(src) and paths.isdir(dst):
            main_deep_copy(src, dst)
        elif paths.isfile(src) and paths.isfile(dst):
            main_copy(sys.argv[1], sys.argv[2])
        else:
            raise Error('mismatch')

    else:
        sys.stderr.write(HELP)
        raise SystemExit(1)

    raise SystemExit()

if __name__ == '__main__':
    main()
