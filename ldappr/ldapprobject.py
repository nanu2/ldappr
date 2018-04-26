import ldap
import ldif
from ldap.cidict import cidict
from io import StringIO
from uuid import UUID

class CustomCidict(cidict):
    def __getitem__(self, key):
        """Override of the __getitem__ method to return an empty list if a key
        does not exist (instead of raising an exception)
        """
        if key.lower() in self.data:
            return self.data[key.lower()]
        return []


class LdapprObject(object):
    """\
    The LdapprObject is used to handle search results from the Connection
    class. It's a representation of a single object in the LDAP Directory.
    """
    guid = None
    def __init__(self, result, conn):
        """The class is initialized with a tuple: (dn, {attributes}), and the
        existing connection
        """
        (self.dn, self.attributes) = result
        self.attrs = CustomCidict(self.attributes)
        if 'objectguid' in [x.lower() for x in list(self.attrs.keys())]:
            self.guid = str(UUID(bytes=self.attrs['objectguid'][0]))
        self.conn = conn

    def __str__(self):
        """Pretty prints all attributes with values."""
        col_width = max(len(key) for key in list(self.attrs.keys()))
        pretty_string = '{attr:{width}} : {value}\n'.format(
            attr='dn', width=col_width, value=self.dn)
        for key, value in list(self.attrs.items()):
            if len(str(value[0])) > 80:  # hack to 'detect' binary attrs
                value = ['binary']
            for single_value in value:
                pretty_string += '{attr:{width}} : {value}\n'.format(
                    attr=self._case(key), width=col_width, value=single_value)
                key = ''
        return pretty_string

    def _case(self, attr):
        """Transforms an attribute to correct case (e.g. gIvEnNaMe becomes
        givenName). If attr is unknown nothing is transformed.

        :param attr: may be incorrectly cased
        :return: attr in proper case
        """
        try:
            index = [x.lower() for x in list(self.attrs.keys())].index(attr.lower())
            return list(self.attrs.keys())[index]
        except:
            return attr

    def to_ldif(self):
        """Makes LDIF of ldappr object."""
        out = StringIO()
        ldif_out = ldif.LDIFWriter(out)
        ldif_out.unparse(self.dn, self.attributes)
        return out.getvalue()

    def set_value(self, attr, value):
        attr = self._case(attr)
        self.conn.modify_s(self.dn, [(ldap.MOD_REPLACE, attr, value)])
        self.attrs[attr] = [value]

    def add_value(self, attr, value):
        attr = self._case(attr)
        self.conn.modify_s(self.dn, [(ldap.MOD_ADD, attr, value)])
        self.attrs[attr].append(value)

    def remove_value(self, attr, value):
        attr = self._case(attr)
        self.conn.modify_s(self.dn, [(ldap.MOD_DELETE, attr, value)])
        if value in self.attrs[attr]:
            self.attrs[attr].remove(value)
