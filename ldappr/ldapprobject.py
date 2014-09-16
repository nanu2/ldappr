import ldap
import ldif
from ldap.cidict import cidict
from StringIO import StringIO


class LdapprObject(object):
    """\
    The LdapprObject is used to handle search results from the Connection
    class. It's a representation of a single object in the LDAP Directory.
    """
    def __init__(self, result, conn):
        """The class is initialized with a tuple: (dn, {attributes}), and the
        existing connection.
        """
        (self.dn, self.attributes) = result
        self.attrs = cidict(self.attributes)
        self.conn = conn

    def __str__(self):
        """Pretty prints all attributes with values."""
        col_width = max(len(key) for key in self.attrs.keys())
        pretty_string = '{attr:{width}} : {value}\n'.format(
                attr='dn', width=col_width, value=self.dn)
        for key, value in self.attrs.iteritems():
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
            index = [x.lower() for x in self.attrs.keys()].index(attr.lower())
            return self.attrs.keys()[index]
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
