# server/webapp/db/execution.py

import traceback

class SQLExecutorMixin:
    def _db_execute(self, db_cursor, query, params=None):
        try:
            print(f"[DEBUG] Executing query: {query}", flush=True)
            if params:
                print(f"[DEBUG] With params: {params}", flush=True)
                out = db_cursor.execute(query, params)
            else:
                out = db_cursor.execute(query)
            return out
        except Exception as e:
            print(f"[ERROR] MySQL execution failed: {e}", flush=True)
            traceback.print_exc()
            raise
