pluginloader.py tests
=====================

The pluginloader.py module has the following functions that need to be tested:

#. `gen_register_list()`_
#. `gen_plugin_list()`_
#. `init_plugin_system()`_

Settings things up
-------------------

First, we do the required imports.

    >>> import src.pluginloader as pl

Next, we create a few mock modules that would provide services and require others.

    >>> class Mock(object):
    ...    def __repr__(self):
    ...        return "requires = " + str(self.requires) +\
    ...               "  provided = " + str(self.provides) + "\n"
    >>> class Requires_Mock(Mock):
    ...    def __init__(self, aSet):
    ...         self.requires = set()
    ...         self.provides = set()
    ...         for item in aSet:
    ...             self.requires.add(item)
    >>> class Provides_Mock(Mock):
    ...    def __init__(self, aSet):
    ...         self.requires = set()
    ...         self.provides = set()
    ...         for item in aSet:
    ...             self.provides.add(item)
    >>> class Both_Mock(Mock):
    ...    def __init__(self, aSet, bSet):
    ...         self.provides = set()
    ...         for item in aSet:
    ...             self.provides.add(item)
    ...         self.requires = set()
    ...         for item in bSet:
    ...             self.requires.add(item)


Next, we define a basic test function for ensuring the ordering was well
done.

    >>> def test_ordering(aList):
    ...     provided_so_far = []
    ...     for item in aList:
    ...         provided_so_far.extend(list(item.provides))
    ...         for i in list(item.requires):
    ...             if i not in provided_so_far:
    ...                 print("ordering problem in gen_register_list")
    ...                 print("provided so far: " + str(provided_so_far))
    ...                 print("required here: " + str(item.requires))


We then define a few mock object that we will use in tests.

    >>> req_b = Requires_Mock(['B'])
    >>> prov_b_c = Provides_Mock(['B', 'C'])
    >>> req_c_g_prov_d_e_f = Both_Mock(['D', 'E', 'F'], ['C', 'G'])
    >>> prov_g = Provides_Mock(['G'])
    >>> req_g_c = Requires_Mock(['G', 'C'])


.. _`gen_register_list()`:

Testing get_register_list()
----------------------------

The first test is one in which an object "b" is provided and required.
It should pass silently.

    >>> set_a = set(); set_a.add(req_b); set_a.add(prov_b_c)
    >>> a_list = pl.gen_register_list(set_a)
    >>> test_ordering(a_list)

We can see the object required appearing after being provided in the final
list:

    >>> ans = "[requires = set([])  provided = set(['C', 'B'])\n, requires = set(['B'])  provided = set([])\n]"
    >>> str(a_list) == ans
    True

The next test is one in which an object "b" is required but not provided.

    >>> set_a = set(); set_a.add(req_b)
    >>> a_list = pl.gen_register_list(set_a)
    >>> test_ordering(a_list)

After it passes silently, we can inspect visually the final list, which
should be empty as the object requiring "b" is removed since "b" is
not provided.

    >>> print(str(a_list))
    []


The next test is one in which an object "b" is not required but is provided.

    >>> set_a = set(); set_a.add(prov_g)
    >>> a_list = pl.gen_register_list(set_a)
    >>> test_ordering(a_list)

After it passes silently, we can inspect visually the final list, which
should should contain that one object.

    >>> ans = "[requires = set([])  provided = set(['G'])\n]"
    >>> str(a_list) == ans
    True



The final test in this series is one in which we add all objects created
so far.

    >>> set_a = set(); set_a.add(req_g_c); set_a.add(req_b)
    >>> set_a.add(req_c_g_prov_d_e_f); set_a.add(prov_g); set_a.add(prov_b_c)
    >>> a_list = pl.gen_register_list(set_a)
    >>> test_ordering(a_list)

.. _`gen_plugin_list()`:

Testing gen_plugin_list()
--------------------------

To do.

.. _`init_plugin_system()`:

Testing init_plugin_system()
-----------------------------

To do.