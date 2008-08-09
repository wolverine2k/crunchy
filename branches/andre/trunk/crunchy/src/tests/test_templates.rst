templates.py tests
================================

templates.py is a plugin whose purpose is to create templates from
existing html files and/or use them in conjunction with another file.  
It has the following functions that require testing:

#. `register()`_



Setting things up
--------------------

    >>> import os
    >>> base_dir = os.getcwd()
    >>> from src.interface import Element, SubElement, tostring, config, from_comet
    >>> config.clear()
    >>> from_comet.clear()
    >>> config['crunchy_base_dir'] = base_dir
    >>> def ignore(*args):
    ...    return
    >>> from_comet['register_new_page'] = ignore
    >>> import src.plugins.templates as templates


Testing create_template()
--------------------------

    >>> handle = open(os.path.join(base_dir, "server_root", "index.html"))
    >>> templates.create_template('a_name', 'user_name', handle)
    >>> print templates._templates #doctest: +ELLIPSIS
    {'a_name': <src.vlam.BasePage object at ...}
    >>> print templates._templates['a_name'].username
    user_name


Testing merge_with_template()
-----------------------------

    >>>

Testing merge_elements()
-------------------------

    >>> template = Element("main")
    >>> head = SubElement(template, "head")
    >>> title = SubElement(head, "title")
    >>> title.text = "This is the title.\n"
    >>> body = Element("body")
    >>> template.append(body)
    >>> div1 = Element("div", id="not this one")
    >>> p1 = Element("p")
    >>> p1.text = "\nKeep this.\n"
    >>> div1.append(p1)
    >>> div2 = Element("div", id="content")
    >>> p2 = Element("p")
    >>> p2.text = "\nThis is part of the target.\n"
    >>> div2.append(p2)
    >>> div3 = Element("div", id="not that one")
    >>> p3 = Element("p")
    >>> p3.text = "\nThis should be kept.\n"
    >>> div3.append(p3)
    >>> body.append(div1)
    >>> body.append(div2)
    >>> body.append(div3)
    >>> print tostring(template)
    <main><head><title>This is the title.
    </title></head><body><div id="not this one"><p>
    Keep this.
    </p></div><div id="content"><p>
    This is part of the target.
    </p></div><div id="not that one"><p>
    This should be kept.
    </p></div></body></main>

    >>> to_combine = Element("main")
    >>> head = SubElement(to_combine, "head")
    >>> title = SubElement(head, "title")
    >>> title.text = "This is the second title.\n"
    >>> body = Element("body")
    >>> to_combine.append(body)
    >>> div1a = Element("div", id="not this one")
    >>> p1a = Element("p")
    >>> p1a.text = "\nThis should be discarded.\n"
    >>> div1a.append(p1a)
    >>> div2a = Element("div", id="content")
    >>> p2a = Element("p")
    >>> p2a.text = "\nThis should be added.\n"
    >>> div2a.append(p2a)
    >>> div3a = Element("div", id="not that one")
    >>> p3a = Element("p")
    >>> p3a.text = "\nThis also should be discarded.\n"
    >>> div3a.append(p3a)
    >>> body.append(div1a)
    >>> body.append(div2a)
    >>> body.append(div3a)
    >>> print tostring(to_combine)
    <main><head><title>This is the second title.
    </title></head><body><div id="not this one"><p>
    This should be discarded.
    </p></div><div id="content"><p>
    This should be added.
    </p></div><div id="not that one"><p>
    This also should be discarded.
    </p></div></body></main>

    >>> target_head = to_combine.find(".//head") # normally, clear title...
    >>> template_head = template.find(".//head")
    >>> new_head = templates.merge_elements(template_head, target_head)
    >>> print tostring(new_head)
    <head><title>This is the title.
    </title><title>This is the second title.
    </title></head>

Testing remove_subelement()

Now, let's clear the template title first...
    >>> template_head = templates.remove_subelement(template.find(".//head"), 'title')
    >>> print tostring(template_head)
    <head />

