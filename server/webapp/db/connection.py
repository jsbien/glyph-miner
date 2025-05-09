# server/webapp/db/connection.py

# server/webapp/db/connection.py

import MySQLdb
import MySQLdb.cursors

class MySQLDB:
    def __init__(self, db=None, user=None, pw=None, host='localhost', port=3306, **kwargs):
        self.db = db
        self.user = user
        self.pw = pw
        self.host = host
        self.port = port
        self.connection = self._connect()

    def _connect(self):
        return MySQLdb.connect(
            db=self.db,
            user=self.user,
            passwd=self.pw,
            host=self.host,
            port=self.port,
            cursorclass=MySQLdb.cursors.DictCursor,
        )

    def get_cursor(self):
        return self.connection.cursor()

    def query(self, sql, params=None):
        cur = self.get_cursor()
        cur.execute(sql, params or ())
        results = cur.fetchall()
        cur.close()
        return results

    def insert(self, table, **fields):
        keys = ', '.join(fields.keys())
        placeholders = ', '.join(['%s'] * len(fields))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        params = list(fields.values())
        cur = self.get_cursor()
        cur.execute(sql, params)
        self.connection.commit()
        cur.close()

    def update(self, table, where, **fields):
        set_clause = ', '.join([f"{k}=%s" for k in fields])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = list(fields.values())
        cur = self.get_cursor()
        cur.execute(sql, params)
        self.connection.commit()
        cur.close()

    def select(self, table, where=None, params=None):
        sql = f"SELECT * FROM {table}"
        if where:
            sql += f" WHERE {where}"
        cur = self.get_cursor()
        cur.execute(sql, params or ())
        results = cur.fetchall()
        cur.close()
        return results
