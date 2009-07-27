
# Written as a Python 3 script for practice :-)
import sys
import os
import os.path as paths

# Help message printed to STDERR when requested in main().
HELP = """\
NAME
pygments2to3.py

USAGE
* python[3.x] pygments2to3.py {pygments3_dir}
  Replaces all instances of "pygments" by "pygments3" in python files unless
  it has already been done.  The python files are found in the directory
  that is passed as an argument.
"""

def update_files(pyg_dir):
    '''Finds all python files and makes the substitution from
    pygments to pygments3 - if it has not already been done.
    (It is assumed that "pygments3" would never occur otherwise.)
    '''
    for root, dirs, files in os.walk(pyg_dir):
        if '.svn' in dirs:
            dirs.remove('.svn')

        for file in files:
            base, ext = paths.splitext(file)
            if ext == ".py":
                fname = paths.join(root, file)
                content = open(fname).read()
                if "pygments3" in content:
                    print('File {} has already been transformed.'.format(fname))
                elif "pygments" not in content:
                    print('"pygments" not found in {}.'.format(fname))
                else:
                    content = content.replace("pygments", "pygments3")
                    new_file = open(fname, "w")
                    new_file.write(content)
                    new_file.close()
                    print('File {} has now been transformed.'.format(fname))
    return


def main():
    """Parses command-line arguments and raises the appropriate
    SystemExit exception."""

    argv = sys.argv
    if '--help' in argv or '-h' in argv or len(argv) == 1:
        sys.stderr.write(HELP)
        raise SystemExit(2)

    if len(sys.argv) == 2:
        pyg_dir = sys.argv[1]
        if paths.isdir(pyg_dir):
            update_files(pyg_dir)
        else:
            print("The argument passed is not a directory.")
            raise SystemExit()
    else:
        print("Wrong number of arguments.\n")
        sys.stderr.write(HELP)

        raise SystemExit()

    print("Done!")
    raise SystemExit()

if __name__ == '__main__':
    main()