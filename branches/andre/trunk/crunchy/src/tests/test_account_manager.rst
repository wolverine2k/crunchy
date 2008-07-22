account_manager.py tests
================================


We start our tests with a non-existing file to be created from scratch.

    >>> import os
    >>> new_file = os.path.join(os.getcwd(), "_temporary_test_file.pwd")
    >>> if os.path.exists(new_file):
    ...     os.remove(new_file)
    >>> import account_manager as am
    >>> accounts = am.Accounts(new_file) # doctest: +ELLIPSIS
    New password file [path = ...] will be created.

Adding a user.

    >>> accounts['user1'] = ('home1', 'password1')
    >>> accounts.save()

Retrieving the stored information using the defined methods.
    >>> encoded_password = accounts.get_password('user1')
    >>> print encoded_password
    ac50c86cc6b773c77b336d9bd3936e3a
    >>> 'home1' == accounts.get_home_dir('user1')
    True

Retrieving the stored information in the saved file.

    >>> pwd_file = open(new_file)
    >>> name1, home1, encoded1 = pwd_file.readline().split(accounts.separator)
    >>> pwd_file.close()
    >>> encoded1 == encoded_password
    True
    >>> name1 == 'user1'
    True
    >>> home1 == 'home1'
    True

Attempt to retrieve a non-existent value.

    >>> "" == accounts.get_password('user2')
    True
    >>> "" == accounts.get_home_dir('user2')
    True

Create a second user.

    >>> accounts['user2'] = ('home2', 'password2')
    >>> accounts.save()

Retrieve the whole existing information by creating a new instance; this will
test the load method indirectly

    >>> accounts_2 = am.Accounts(new_file)
    >>> accounts_2.get_password('user1') == accounts.get_password('user1')
    True
    >>> accounts_2.get_password('user2') == accounts.get_password('user2')
    True

Final cleanup

    >>> os.remove(new_file)


