# server/database/connection.py

import datetime
import MySQLdb
import MySQLdb.cursors
from contextlib import closing
import server.webapp as web

# --- Optional debug log for noisy output ---

from pathlib import Path

log_path = Path("../logs")
log_path.mkdir(exist_ok=True)

DEBUG_LOG = open(log_path / "verbose-debug.log", "a", buffering=1)


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
        try:
            self.connection.ping(reconnect=True)
        except Exception:
            print(">>> Reconnecting to MySQL", file=DEBUG_LOG, flush=True)
            self.connection = self._connect()
        return self.connection.cursor(PatchedDictCursor)

    def query(self, sql, params=None, vars=None):
        print(f">>> QUERY: {sql}", file=DEBUG_LOG, flush=True)
        print(f">>> VARS: {vars}", file=DEBUG_LOG, flush=True)
        try:
            if vars:
                for key, value in vars.items():
                    sql = sql.replace(f"${key}", sqlify(value))
            with closing(self.get_cursor()) as cur:
                print(f">>> CURSOR CLASS: {type(cur)}", file=DEBUG_LOG, flush=True)
                cur.execute(sql, params or ())
                result = cur.fetchall()
                print(">>> QUERY SUCCESS", file=DEBUG_LOG, flush=True)
                return result
        except Exception as e:
            print(">>> QUERY FAILED:", e, file=DEBUG_LOG, flush=True)
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
            return cur.lastrowid 

    def update(self, table, where, vars=None, **fields):
        set_clause = ', '.join([f"{k} = {sqlify(v)}" for k, v in fields.items()])
        if vars:
            for key, value in vars.items():
                placeholder = f"${key}"
                where = where.replace(placeholder, sqlify(value))
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

        result = self.query(sql)
        self.connection.commit()
        return result
