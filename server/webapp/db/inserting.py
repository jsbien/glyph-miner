# server/webapp/db/inserting.py

from .transaction import transaction

def insert(db_cursor, table, **values):
    keys = ", ".join(values.keys())
    placeholders = ", ".join(["%s"] * len(values))
    query = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
    params = list(values.values())

    print(f"[DEBUG] Executing INSERT: {query}")
    print(f"[DEBUG] With params: {params}")
    db_cursor.execute(query, params)
