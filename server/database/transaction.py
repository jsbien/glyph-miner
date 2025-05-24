from contextlib import contextmanager
import server.webapp as web

# --- Optional debug log for noisy output ---

from pathlib import Path

log_path = Path("../logs")
log_path.mkdir(exist_ok=True)

DEBUG_LOG = open(log_path / "verbose-debug.log", "a", buffering=1)

@contextmanager
def transaction():
    """Context manager for database transaction."""
    db = web.ctx.db
    db_cursor = db.cursor()
    try:
        yield db_cursor
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db_cursor.close()

class MySQLDB:
    def commit(self):
        if self._db:
            try:
                self._db.commit()
                print("[DEBUG] Transaction committed", file=DEBUG_LOG, flush=True)
            except Exception as e:
                print(f"[ERROR] Commit failed: {e}")
                raise

    def rollback(self):
        if self._db:
            try:
                self._db.rollback()
                print("[DEBUG] Transaction rolled back", file=DEBUG_LOG, flush=True)
            except Exception as e:
                print(f"[ERROR] Rollback failed: {e}")
                raise

    # Internal aliases
    _db_commit = commit
    _db_rollback = rollback
