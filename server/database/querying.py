# server/webapp/db/querying.py

def query(self, sql_query, vars=None, processed=False, _test=False):
    print(">>> 🐛 ENTERED db.query() <<<", flush=True)
    cur = self.ctx.db.cursor()
    self._db_execute(cur, sql_query, vars)
    out = cur.fetchall()
    if processed:
        out = [dict(zip([d[0] for d in cur.description], row)) for row in out]
    return out

def select(self, table, what='*', where='1=1', vars=None, _test=False):
    qout = "SELECT %s FROM %s WHERE %s" % (what, table, where)
    return self.query(qout, vars, processed=True, _test=_test)
