# from . import connection
from .connection import MySQLDB

# Registry of supported databases
_databases = {}

def register_database(name, clazz):
    """Registers a database backend class under a name like 'mysql'."""
    _databases[name] = clazz

def database(dburl=None, dbn=None, **params):
    if dbn:
        if dbn == 'mysql':
            return MySQLDB(**params)
        else:
            raise ValueError(f"Unsupported database type: {dbn}")
    elif dburl:
        return MySQLDB(dburl, **params)
    else:
        raise ValueError("Either dburl or dbn must be provided.")
