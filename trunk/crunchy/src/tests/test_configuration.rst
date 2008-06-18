configuration.py tests
======================

configuration.py has a single class with multiple methods.  We will test
these methods following certain themes.

#. directories_
#. dir_help_
#. doc_help


Setting things up
------------------

    >>> from src.configuration import defaults
    >>> import os
    >>> def temp_set_lang(lang, verbose=True):
    ...    current = defaults._Defaults__language
    ...    defaults._set_language(lang, verbose=verbose)
    ...    return current
    >>>

.. _`directories`:

Testing directories
---------------------

First, we call the default function that attempts to create the
user directory and the temporary directory.

    >>> defaults._set_dirs()

Next, we test for the home directory.

    >>> home_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
    >>> print(os.path.exists(home_dir))
    True
    >>> print(home_dir == defaults._get_user_dir())
    True
    >>> # also indirectly testing defaults._get_user_dir()
    >>> print(home_dir == defaults.user_dir)
    True


Next, we test for the temporary directory.

    >>> temp_dir = os.path.join(home_dir, "temp")
    >>> print(os.path.exists(temp_dir))
    True
    >>> print(temp_dir == defaults._get_temp_dir())
    True
    >>> print(temp_dir == defaults.temp_dir)
    True

.. _dir_help:

Testing dir_help
-----------------

Saving initial values, and setting default language to English.

    >>> saved = temp_set_lang('en')
    language set to: en
    editarea_language also set to: en
    >>> current = defaults._get_dir_help()

Proceeding with the tests.

    >>> print(current == defaults._Defaults__dir_help)
    True
    >>> print(current == defaults.dir_help)
    True
    >>> defaults.dir_help = True
    >>> defaults.dir_help == defaults._get_dir_help()
    True
    >>> defaults.dir_help = 'True'
    Invalid choice for crunchy.dir_help
    The valid choices are: [True, False]
    The current value is: True

Now testing with a different language.

    >>> dummy = temp_set_lang('fr') # doctest:+ELLIPSIS
    la valeur ...
    >>> defaults.dir_help = 'junk'
    Choix invalide pour crunchy.dir_help
    Les choix valides sont :[True, False]
    La valeur actuelle est :True

Finally restoring the initial values

    >>> defaults.dir_help = current
    >>> dummy = temp_set_lang(saved, verbose=False)

.. _doc_help:

Testing doc_help
-----------------

Saving initial values, and setting default language to English.

    >>> saved = temp_set_lang('en')
    language set to: en
    editarea_language also set to: en
    >>> current = defaults._get_doc_help()

Proceeding with the tests.

    >>> print(current == defaults._Defaults__doc_help)
    True
    >>> print(current == defaults.doc_help)
    True
    >>> defaults.doc_help = True
    >>> defaults.doc_help == defaults._get_doc_help()
    True
    >>> defaults.doc_help = 'True'
    Invalid choice for crunchy.doc_help
    The valid choices are: [True, False]
    The current value is: True

Now testing with a different language.

    >>> dummy = temp_set_lang('fr') # doctest:+ELLIPSIS
    la valeur ...
    >>> defaults.doc_help = 'junk'
    Choix invalide pour crunchy.doc_help
    Les choix valides sont :[True, False]
    La valeur actuelle est :True

Finally restoring the initial values

    >>> defaults.doc_help = current
    >>> dummy = temp_set_lang(saved, verbose=False)


