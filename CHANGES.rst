Changelog
---------------

0.1.5
+++++

- Override of cidicts __getitem__ so that user.attrs['nonexistent'] won't raise an exception, but instead returns an empty list

0.1.2
+++++

- README.md to README.rst (pypi should show a nice README as well)

0.1.1
+++++

- fixed pretty print of binary attribute
- fixed ldap.get sizelimit=1 exception for now
- added try catch to api

0.1
+++

- Initial version, have to start somewhere