file_service.py tests
=====================


Testing saving and reading from a file.

    >>> import src.plugins.file_service as fs
    >>> import random, os

Generate a totally random file.

    >>> fake_name = "test%d"%random.random()
    >>> content = "content%d"%random.random()

See if we can save it.

    >>> fs.save_file(fake_name, content)
    >>> print(os.path.exists(fake_name))
    True

And if we can read from it.

    >>> print(fs.read_file(fake_name) == content)
    True

Finally, we need to clean up.

    >>> if os.path.exists(fake_name):
    ...       os.remove(fake_name) 
    >>>

