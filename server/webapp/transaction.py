class MySQLDB:
    def commit(self):
        if self._db:
            try:
                self._db.commit()
                print("[DEBUG] Transaction committed")
            except Exception as e:
                print(f"[ERROR] Commit failed: {e}")
                raise

    def rollback(self):
        if self._db:
            try:
                self._db.rollback()
                print("[DEBUG] Transaction rolled back")
            except Exception as e:
                print(f"[ERROR] Rollback failed: {e}")
                raise

    # Internal aliases
    _db_commit = commit
    _db_rollback = rollback
