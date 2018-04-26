import ldap
import ldap.filter
from .ldapprobject import LdapprObject
from uuid import UUID


class Connection(object):
    """Initiates connection with handy methods"""
    def __init__(self, server, protocol='ldap', port='', verify=True,
                 search_base=''):
        self.search_base = search_base
        if port == '':
            port = 389 if protocol == 'ldap' else 636
        self.ldap_url = '{}://{}:{}'.format(protocol, server, str(port))
        try:
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            if not verify:
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,
                                ldap.OPT_X_TLS_NEVER)
            self.conn = ldap.initialize(self.ldap_url)
        except:
            raise

    def type(self):
        result = self.conn.search_s('', ldap.SCOPE_BASE,
                                    attrlist=['objectClass', 'vendorName',
                                              'supportedCapabilities'])
        rootDSE = LdapprObject(result[0], self.conn)
        if rootDSE.attrs['vendorName'] == ['Novell, Inc.']:
            return 'eDirectory'
        if '1.2.840.113556.1.4.800' in rootDSE.attrs['supportedCapabilities']:
            return 'Active Directory'
        if rootDSE.attrs['vendorName'] == ['Apache Software Foundation']:
            return 'Apache DS'
        if 'OpenLDAProotDSE' in rootDSE.attrs['objectClass']:
            return 'OpenLDAP'
        return 'Unknown'

    def search(self, search_filter):
        """Get list of objects that match the search_filter

        :param search_filter: filter to find the objects
        :return: list of LdapperObjects (or empty list)
        """
        search_filter = ldap.filter.escape_filter_chars(search_filter)
        result = self.conn.search_s(self.search_base, ldap.SCOPE_SUBTREE,
                                    search_filter)
        return [LdapprObject(item, self.conn) for item in result if item[0] != None ]
    def search_by_guid(self, guid):
        """Get object that match the objectGuid

        :guid GUID like  XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
        :return: list of LdapperObjects (or empty list)
        """
        u = UUID(guid)
        search_filter = '(objectguid=%s)' % ''.join(['\\%s' % u.hex[i:i+2] for i in range(0, len(u.hex), 2)])
        result = self.conn.search_s(self.search_base, ldap.SCOPE_SUBTREE,
                                    search_filter)
        return [LdapprObject(item, self.conn) for item in result if item[0] != None ]

    def get(self, search_filter):
        """Get first object found

        :param search_filter: filter to find the object
        :return: LdapprObject or None
        """
        # TODO: use sizelimit=1 with proper exception handling
        search_filter = ldap.filter.escape_filter_chars(search_filter)
        result = self.conn.search_ext_s(self.search_base,
                                        ldap.SCOPE_SUBTREE,
                                        search_filter, sizelimit=0)
        return LdapprObject(result[0], self.conn) if result else None

    def get_by_dn(self, dn):
        """Get LdapprObject for known dn

        :param dn: dn of the object we're looking for
        :return: LdapprObject
        """
        result = self.conn.search_s(dn, ldap.SCOPE_BASE)
        return LdapprObject(result[0], self.conn)
        
    def get_dn(self, search_filter):
        """Get list of dn's that match the filter

        :param search_filter: filter to find the dn's
        :return: list of dn's
        """
        search_filter = ldap.filter.escape_filter_chars(search_filter)
        result = self.conn.search_s(self.search_base, ldap.SCOPE_SUBTREE,
                                    search_filter)
        return [dn for (dn, item) in result if item[0] != None]

    def get_values(self, dn, attr):
        """Get list of values of given attribute for dn

        :param dn: dn of the object we're looking for
        :param attr: attribute name (case insensitive)
        :return: list of values
        """
        result = self.conn.search_s(dn, ldap.SCOPE_BASE)
        result_object = LdapprObject(result[0], self.conn)
        return result_object.attrs[attr]

    def get_value(self, dn, attr):
        """Get (first) attr value as string

        :param dn: dn of the object we're looking for
        :param attr: attribute name (case insensitive)
        :return: value as string
        """
        result = self.get_values(dn, attr)
        return result[0]

    def verify_password(self, dn, password):
        try:
            test_conn = ldap.initialize(self.ldap_url)
            test_conn.simple_bind_s(dn, password)
            test_conn.unbind_s()
        except ldap.LDAPError:
            return False
        return True

    def close(self):
        self.conn.unbind_s()


class AuthConnection(Connection):
    def __init__(self, server, bind_dn, password, **kwargs):
        super(AuthConnection, self).__init__(server, **kwargs)
        try:
            self.conn.simple_bind_s(bind_dn, password)
        except ldap.LDAPError:
            raise

    def add(self, dn, modlist):
        """Adds an entry to the LDAP store

        :param dn: dn of the new entry
        :param modlist: list of attributes made up of two-value tuples, where
            the first item of each tuple is the attribute name, and the
            second value is a list of attribute values.
        """
        self.conn.add_s(dn, modlist)

    def modify(self, dn, modlist):
        self.conn.modify_s(dn, modlist)

    def set_value(self, dn, attr, value):
        self.conn.modify_s(dn, [(ldap.MOD_REPLACE, attr, value)])

    def add_value(self,  dn, attr, value):
        self.conn.modify_s(dn, [(ldap.MOD_ADD, attr, value)])

    def delete_value(self, dn, attr, value):
        self.conn.modify_s(dn, [(ldap.MOD_DELETE, attr, value)])

    def delete(self, dn):
        self.conn.delete_s(dn)
