Ldappr
======

|PyPI version|

| Ldappr is a wrapper around python-ldap, meant for quick and easy
handling of
| common administrative tasks concerning your LDAP compliant repository.
It is
| particularly useful in small, one-time scripts to get things done, or
| interactively within an iPython shell.

Installation
------------

Of course, python-ldap is supposed to be already installed.

::

    pip install ldappr

Connect
-------

.. code:: python

    import ldappr

    # authenticated bind
    ldap = ldappr.connect_to('127.0.0.1', 'uid=admin,ou=system', 'secret')

Retrieve objects
----------------

When you have a connection, you can search on it. First, specify the
seach base.

.. code:: python

    ldap.search_base = 'ou=users,ou=system'

Then, get one or more objects to manipulate.

.. code:: python

    # retrieve a single object
    user = ldap.get('cn=jdoe')

    # retrieve a list of objects
    users = ldap.search('objectClass=inetOrgPerson')

Do stuff
--------

| Once you got an object, you can easily manipulate it. All changes will
| immediately reflect in your LDAP repository.

.. code:: python

    # pretty print the retrieved user
    print(user)

    # get an attribute value
    sn = user.attrs['sn']

    # set an attribute value (existing value will be removed)
    user.set_value('givenName', 'Jack')

    # add a value to a multi-valued attribute
    user.add_value('mobile', '0123456789')
    user.add_value('mobile', '9876543210')

    # remove a value from a multi-valued attribute
    user.remove_value('mobile', '9876543210')

Other examples
--------------

.. code:: python

    # anonymous bind
    ldap = ldappr.connect_to('127.0.0.1')

    # authenticated bind with more options
    ldap = ldappr.connect_to('127.0.0.1', 'uid=admin,ou=system', 'secret',
                              protocol='ldaps', port='10636', verify=False, 
                              search_base='ou=users,ou=system')

    # delete all objects with employeeType manager
    for dn in ldap.get_dn('employeeType=manager'):
        ldap.delete(dn)

    # set an attribute value for a known dn
    ldap.set_value('cn=jdoe,ou=users,ou=system', 'givenName', 'Jack')

    # make an LDIF export for all users
    with open('export.ldif', 'a') as file:
        for user in ldap.search('objectClass=inetOrgPerson'):
            file.write(user.to_ldif())

.. |PyPI version| image:: https://badge.fury.io/py/ldappr.svg
   :target: http://badge.fury.io/py/ldappr

