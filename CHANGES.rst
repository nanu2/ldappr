Changelog
---------------

0.2.0
+++++

**Improvements**
- Added verify_password(dn, password) method

**Bugfixes**
- Added escape_filter_chars() to filter (sanitize) the filter
- Override of cidicts __getitem__ so that user.attrs['nonexistent'] won't raise an exception, but instead returns an empty list

0.1.3 and 0.1.4
+++++++++++++++

- Wrestling with pypi (needs a new version number even if you've made a mistake by uploading rubbish)

0.1.2
+++++

- Converted README.md to README.rst (pypi should show a nice README as well)

0.1.1
+++++

**Bugfixes**
- Fixed pretty print of binary attribute
- Fixed ldap.get sizelimit=1 exception for now (come back to this later)
- Added try catch to api

0.1.0
+++++

- Initial version (have to start somewhere)