import MySQLdb
import MySQLdb.cursors

class MySQLDB:
    def __init__(self, dbn, user, pw, db, host='localhost', port=3306, charset='utf8mb4'):
        self.dbn = dbn
        self.user = user
        self.pw = pw
        self.db = db
        self.host = host
        self.port = port
        self.charset = charset
        self._db = None
        self._cursor = None
        self.connect()

    def connect(self):
        if self.dbn != 'mysql':
            raise ValueError("Only MySQL is currently supported")
        self._db = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.pw,
            db=self.db,
            port=self.port,
            charset=self.charset,
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor
        )
        self._cursor = self._db.cursor()
        print("[DEBUG] MySQLDB connected")

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._db:
            self._db.close()
        print("[DEBUG] MySQLDB connection closed")

    def __del__(self):
        self.close()

     # In server/webapp/db/base.py
# import server.webapp.db.connection as conn

_databases = {}

from . import connection as conn

def database(dburl=None, **params):
    return conn.get_connection(dburl, **params)


# # Assuming the MySQLDB or equivalent connection class was in connection.py
# def database(dburl=None, **params):
#     """ Returns a database connection instance """
#     if dburl is None:
#         dburl = "default_database_url"  # You can change this to your default
#     return conn.MySQLdb(dburl, **params)  # Assuming MySQLDB is in connection.py

# Registering databases (if necessary)
def register_database(name, clazz):
    """ Register a database instance by name """
    _databases[name] = clazz
   
