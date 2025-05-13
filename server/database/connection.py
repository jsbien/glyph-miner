# server/database/connection.py

import datetime
import MySQLdb
import MySQLdb.cursors
from contextlib import closing

class PatchedDictCursor(MySQLdb.cursors.DictCursor):
    def close(self):
        try:
            if not self._executed:
                return
            if hasattr(self, '_result') and self._result:
                self._result = None
        except Exception:
            pass

def sqlify(obj):
    if obj is None:
        return 'NULL'
    elif obj is True:
        return "'t'"
    elif obj is False:
        return "'f'"
    elif isinstance(obj, datetime.datetime):
        return repr(obj.isoformat())
    else:
        return repr(obj)

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
        return self.connection.cursor(PatchedDictCursor)

    def query(self, sql, params=None, vars=None):
        print(f">>> QUERY: {sql}")
        print(f">>> VARS: {vars}")
        try:
            if vars:
                for key, value in vars.items():
                    sql = sql.replace(f"${key}", sqlify(value))
            with closing(self.get_cursor()) as cur:
                cur.execute(sql, params or ())
                result = cur.fetchall()
                print(">>> QUERY SUCCESS")
                return result
        except Exception as e:
            print(">>> QUERY FAILED:", e)
            raise

    def select(self, table, vars=None, where=None):
        sql = f"SELECT * FROM {table}"
        if where:
            sql += f" WHERE {where}"
        return self.query(sql, vars=vars)

    def insert(self, table, **fields):
        keys = ', '.join(fields.keys())
        placeholders = ', '.join(['%s'] * len(fields))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        params = list(fields.values())
        with closing(self.get_cursor()) as cur:
            cur.execute(sql, params)
            self.connection.commit()

    def update(self, table, where, **fields):
        set_clause = ', '.join([f"{k}=%s" for k in fields])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = list(fields.values())
        with closing(self.get_cursor()) as cur:
            cur.execute(sql, params)
            self.connection.commit()
