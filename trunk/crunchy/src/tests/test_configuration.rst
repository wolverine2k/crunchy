configuration.py tests
======================


This file contains tests of configuration options.  It is very, very far from being
complete - more like a stub.

    >>> from src.configuration import defaults
    >>> import os
    >>> home_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
    >>> print(os.path.exists(home_dir))
    True
    >>> print(home_dir == defaults.user_dir)
    True
    >>> temp_dir = os.path.join(home_dir, "temp")
    >>> print(os.path.exists(temp_dir))
    True
