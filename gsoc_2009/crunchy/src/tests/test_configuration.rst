configuration.py tests
======================


Setting things up
------------------

    >>> from src.interface import config, plugin
    >>> plugin.clear()
    >>> config.clear()
    >>> from os import getcwd
    >>> config['crunchy_base_dir'] = getcwd()
    >>> from src.configuration import Base, make_property, options

Sample use of extending the Base class for a single object:


    >>> options.update( { 'y': [True, False],
    ...             'x': [1, 2, 4, 8]})
    >>> class Simple(Base):
    ...    def __init__(self, prefs):
    ...        self._preferences = prefs
    ...        self._preferences.update( {'_prefix': 'crunchy'})
    ...        self._init_properties(Simple)
    ...    def _save_settings(self, name, value, initial=False):
    ...        if not initial:
    ...            print "Saving", name, '=', value
    ...        self._preferences[name] = value
    ...    y = make_property('y')
    ...    x = make_property('x')
    
    >>>
    >>> a_dict = {}
    >>> example = Simple(a_dict)
    >>> example.y = 3
    3 is an invalid choice for crunchy.y
    The valid choices are: [True, False]
    The current value is: True
    >>> example.y = False
    Saving y = False
    >>> print a_dict == example._preferences
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

    

