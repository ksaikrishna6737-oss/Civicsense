"""Tiny SQLite storage for the CivicSense app (one table: complaints)."""
import os
import sqlite3
from datetime import datetime, date
import pandas as pd

DB_PATH = os.environ.get("CIVICSENSE_DB", "civicsense.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL, location TEXT, lat REAL NOT NULL, lon REAL NOT NULL,
            created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Received', photo TEXT)""")


def add(text, location, lat, lon, photo=None, created_at=None):
    with _conn() as c:
        cur = c.execute("INSERT INTO complaints (text, location, lat, lon, created_at, photo) VALUES (?,?,?,?,?,?)",
                        (text, location, lat, lon, (created_at or datetime.now()).isoformat(), photo))
        return cur.lastrowid


def add_many(df):
    with _conn() as c:
        c.executemany("INSERT INTO complaints (text, location, lat, lon, created_at) VALUES (?,?,?,?,?)",
                      [(r.text, r.location, float(r.lat), float(r.lon), r.created_at.isoformat()) for r in df.itertuples()])


def _read(where=""):
    with _conn() as c:
        return pd.read_sql_query("SELECT * FROM complaints " + where, c, parse_dates=["created_at"])


def all_complaints():
    return _read()


def open_complaints():
    return _read("WHERE status != 'Resolved'")


def get(cid):
    df = _read(f"WHERE id = {int(cid)}")
    return None if df.empty else df.iloc[0]


def set_status(ids, status):
    with _conn() as c:
        c.executemany("UPDATE complaints SET status = ? WHERE id = ?", [(status, int(i)) for i in ids])


def delete_all():
    with _conn() as c:
        c.execute("DELETE FROM complaints")


def signature():
    """Changes whenever the data changes; used as the cache key for the (slowish) analysis."""
    with _conn() as c:
        row = c.execute("SELECT COUNT(*), COALESCE(MAX(id),0), COALESCE(SUM(status='Resolved'),0), "
                        "COALESCE(SUM(status='Assigned'),0) FROM complaints").fetchone()
    return tuple(row) + (date.today().isoformat(),)
