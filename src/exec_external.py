import os
from popen2 import popen2
from subprocess import Popen
def exec_external(code, console=False):
    """execute code in an external process
    currently works under: 
        * Windows NT (tested)
        * GNOME (tested)
    This also needs to be implemented for OS X, KDE 
    and some form of linux fallback (xterm?)
    """
    file = open("temp.py", 'w')
    file.write(code)
    file.close()
    if os.name == 'nt':
        if console:
            win_run("cmd", ('/c start python temp.py'))
        else:
            win_run("cmd", ('/c python temp.py'))
    elif os.name == 'posix':
        try:
            os.spawnlp(os.P_NOWAIT, 'gnome-terminal', 'gnome-terminal', '-x', 'python', 'temp.py')
        except:
            raise NotImplementedError
    else:
        raise NotImplementedError

# The following is adapted from "Python Standard Library", by Fredrik Lundh
def win_run(program, *args):
    for path in os.environ["PATH"].split(os.pathsep):
        filename = os.path.join(path, program) + ".exe"
        try:
            return Popen([filename, args])
        except:
            pass
    raise os.error, "cannot find executable"