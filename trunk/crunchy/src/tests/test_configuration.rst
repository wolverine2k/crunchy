configuration.py tests
======================


Setting things up
------------------

    >>> from src.configuration import Base, make_property

Sample use of extending the Base class for a single object:

    >>> class Simple(Base):
    ...    def __init__(self, prefs):
    ...        self.prefs = prefs
    ...        self.prefs.update( {'_prefix': 'crunchy'})
    ...        self.init_properties(Simple)
    ...    def _save_settings(self, name, value, initial=False):
    ...        if not initial:
    ...            print "Saving", name, '=', value
    ...        self.prefs[name] = value
    ...    y = make_property('y', [True, False])
    ...    x = make_property('x', [1, 2, 4, 8])
    
    >>>
    >>> a_dict = {}
    >>> example = Simple(a_dict)
    >>> example.y = 3
    Invalid choice for crunchy.y
    The valid choices are: [True, False]
    The current value is: True
    >>> example.y = False
    Saving y = False
    >>> print a_dict == example.prefs
    True

Multi users examples.
---------------------

    >>> user_names = ['Tao', 'Florian', 'Johannes', 'Andre']
    >>> users = {}
    >>> configs = {}
    >>> for name in user_names: #doctest: +ELLIPSIS
    ...     configs[name] = {}
    ...     users[name] = Simple(configs[name])
    >>> users['Tao'].x = 4
    Saving x = 4
    >>> for name in user_names:
    ...    print users[name].x, 
    4 1 1 1

    

