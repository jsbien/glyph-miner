# server/webapp/db/connection.py

import MySQLdb

class MySQLDB:
    """Simple wrapper around MySQLdb for compatibility with legacy code."""
    def __init__(self, dburl=None, **params):
        self.connection = MySQLdb.connect(**params)
        self.cursor = self.connection.cursor()

    def query(self, sql, params=None):
        """Executes a SELECT-like query and returns results."""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        """Executes a non-SELECT SQL command (INSERT/UPDATE/DELETE)."""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

    def commit(self):
        """Commits the current transaction."""
        self.connection.commit()

    def rollback(self):
        """Rolls back the current transaction."""
        self.connection.rollback()

    def close(self):
        """Closes the DB connection."""
        self.cursor.close()
        self.connection.close()

    def get_cursor(self):
        """Returns the raw cursor (legacy compatibility)."""
        return self.cursor
