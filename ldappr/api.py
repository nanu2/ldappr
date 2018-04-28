import sys
import ldap
from .connection import Connection, AuthConnection


def connect_to(server, *args, **kwargs):
    try:
        if args or 'bind_dn' and 'password' in kwargs:
            return AuthConnection(server, *args, **kwargs)
        return Connection(server, **kwargs)
    except Exception as e:
        print(str(e))

