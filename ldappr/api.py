from connection import Connection, AuthConnection


def connect_to(server, *args, **kwargs):
    if args or 'bind_dn' and 'password' in kwargs:
    #if args:
        return AuthConnection(server, *args, **kwargs)
    return Connection(server, **kwargs)
