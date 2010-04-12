style.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

    >>> from src.interface import plugin, config, get_base_dir
    >>> plugin.clear()
    >>> config.clear()
    >>> config['crunchy_base_dir'] = get_base_dir()
    >>> import src.plugins.style as style


    >>> out = style._style("print 'Hello'", 'python', 'tango')
    >>> print(out)
    <pre>
    <span class="k">print</span> <span class="s">&#39;Hello&#39;</span></pre>
    >>> out = style._style("print u'Hello'", 'python', 'tango')
    >>> print(out)
    <pre>
    <span class="k">print</span> <span class="s">u&#39;Hello&#39;</span></pre>