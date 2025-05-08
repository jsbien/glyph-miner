# server/webapp/db/connection.py

import MySQLdb
import os

class DBConnectionMixin:
    def _db_connect(self):
        return MySQLdb.connect(
            host=os.environ.get("GLYPH_DB_HOST", "localhost"),
            user=os.environ.get("GLYPH_DB_USER", "glyph"),
            passwd=os.environ.get("GLYPH_DB_PASSWORD", "glyph"),
            db=os.environ.get("GLYPH_DB_NAME", "glyph"),
            charset="utf8",
        )
