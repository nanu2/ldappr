import unittest
from ldappr import connect_to


class TestLdappr(unittest.TestCase):
    def setUp(self):
        """SetUp method is called for every testcase. We're stretching the
        boundaries here, because we create an account, thus making the setUp
        method a test in itself.

        Current parameters are consistent with a default LDAP server install
        with Apache Directory Studio on local machine.
        """
        self.server = '127.0.0.1'
        self.bind_dn = 'uid=admin,ou=system'
        self.password = 'secret'
        self.search_base = 'ou=users,ou=system'
        self.ldap_port = 10389
        self.ldaps_port = 10636
        self.ldap = connect_to(self.server, self.bind_dn, self.password,
                               protocol='ldaps', port=self.ldaps_port,
                               verify=False, search_base=self.search_base)
        self.new_dn = 'cn=jdoe,' + self.search_base
        self.modlist = [
            ('objectClass', ['top', 'inetOrgPerson']),
            ('givenName', ['John']),
            ('sn', ['Doe']),
        ]
        self.ldap.add(self.new_dn, self.modlist)

    def tearDown(self):
        """TearDown method is called after every testcase. The account from
        the setUp method is now deleted. This is another implicit testcase:
        if the delete won't succeed we get an error with the next setUp call.
        """
        self.ldap.delete(self.new_dn)
        self.ldap.close()

    def test_anonymous_bind(self):
        ldap = connect_to(self.server, port=self.ldap_port)
        ldap.close()

    def test_get_attributes_from_ldappr_object(self):
        user = self.ldap.get('cn=jdoe')
        self.assertEqual(user.attrs['givenname'], ['John'])
        self.assertEqual(user.attrs['gIvEnNaMe'], ['John'])

    def test_get_nonexisting_attribute_from_ldappr_object(self):
        user = self.ldap.get('cn=jdoe')
        self.assertEqual(user.attrs['nonexisting'], [])

    def test_search_instead_of_get(self):
        self.assertNotEqual(self.ldap.search('cn=jdoe'), [])

    def test_search_and_find_nothing(self):
        self.assertEqual(self.ldap.search('cn=non-existent'), [])

    def test_pretty_print(self):
        user = self.ldap.get('cn=jdoe')
        user_string = """\
dn          : cn=jdoe,""" + self.search_base + """
objectClass : organizationalPerson
            : person
            : inetOrgPerson
            : top
givenName   : John
cn          : jdoe
sn          : Doe
"""
        self.assertEqual(user.__str__(), user_string)

    def test_print_ldif(self):
        user = self.ldap.get('cn=jdoe')
        user_ldif = """\
dn: cn=jdoe,""" + self.search_base + """
cn: jdoe
givenName: John
objectClass: organizationalPerson
objectClass: person
objectClass: inetOrgPerson
objectClass: top
sn: Doe

"""
        self.assertEqual(user.to_ldif(), user_ldif)

    def test_get_attribute_values_from_dn(self):
        value = self.ldap.get_value(self.new_dn, 'sn')
        self.assertEqual(value, 'Doe')
        value = self.ldap.get_values(self.new_dn, 'sn')
        self.assertEqual(value, ['Doe'])

    def test_get_dnlist(self):
        dnlist = self.ldap.get_dn('cn=jdoe')
        self.assertEqual(dnlist, ['cn=jdoe,' + self.search_base])

    def test_set_value(self):
        user = self.ldap.get_by_dn(self.new_dn)
        user.set_value('givenName', 'Jack')
        self.assertEqual(user.attrs['givenName'], ['Jack'])
        user = self.ldap.get_by_dn(self.new_dn)
        self.assertEqual(user.attrs['givenName'], ['Jack'])
        self.ldap.set_value(self.new_dn, 'givenName', 'John')
        user = self.ldap.get_by_dn(self.new_dn)
        self.assertEqual(user.attrs['givenName'], ['John'])

    def test_add_value(self):
        user = self.ldap.get_by_dn(self.new_dn)
        user.set_value('mobile', '0123456789')
        user.add_value('mobile', '9876543210')
        self.assertEqual(user.attrs['mobile'], ['0123456789', '9876543210'])
        user = self.ldap.get_by_dn(self.new_dn)
        self.assertEqual(user.attrs['mobile'], ['0123456789', '9876543210'])

    def test_remove_value(self):
        user = self.ldap.get_by_dn(self.new_dn)
        user.set_value('mobile', '0123456789')
        user.add_value('mobile', '9876543210')
        user.remove_value('mobile', '0123456789')
        self.assertEqual(user.attrs['mobile'], ['9876543210'])
        user = self.ldap.get_by_dn(self.new_dn)
        self.assertEqual(user.attrs['mobile'], ['9876543210'])

    def test_verify_password(self):
        self.assertEqual(self.ldap.verify_password(self.bind_dn,
                                                   self.password), True)
        self.assertEqual(self.ldap.verify_password(self.bind_dn,
                                                   'wrong_password'), False)

if __name__ == '__main__':
    unittest.main()
