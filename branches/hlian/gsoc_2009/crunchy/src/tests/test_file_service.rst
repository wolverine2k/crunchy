file_service.py tests
=====================


Testing saving and reading from a file.

    >>> import random
    >>> import os
    >>> import src.plugins.file_service as fs
    >>> import src.tests.mocks as mocks

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

Test ``filtered_dir``, specifically the requirement that it pass
bytestrings to ``request.wfile`` rather than Unicode::

    >>> req = mocks.Request(data=u'dir=gibberish')
    >>> fs.filtered_dir(req, afilter=lambda x, y: False)
    >>> joiner = u''.encode()
    >>> print joiner.join(req.wfile.lines).decode('utf8')
    <ul class="jqueryFileTree" style="display: none;">Could not load directory: [Errno 2] No such file or directory: 'gibberish'</ul>
