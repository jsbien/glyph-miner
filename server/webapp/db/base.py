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
