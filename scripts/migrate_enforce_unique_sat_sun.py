#!/usr/bin/env python3
"""Idempotent migration to enforce UNIQUE(staff_id) on sat and sun tables.

This script will:
- create new tables `sat_new` and `sun_new` with UNIQUE(staff_id)
- copy deduplicated rows from `sat`/`sun` into the new tables (keep MAX(is_evection))
- drop the old tables and rename the new ones

It is safe to run multiple times. It creates a backup file before making changes.
"""
import shutil
import sqlite3
from pathlib import Path


DB_PATH = Path('instance') / 'weekend-overtime.sqlite'


def run():
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH}")
        return

    backup = DB_PATH.with_suffix('.sqlite.bak')
    print(f"Backing up {DB_PATH} -> {backup}")
    shutil.copy2(DB_PATH, backup)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Helper to migrate one table
    def migrate_day(day):
        new = f"{day}_new"
        print(f"Migrating {day} -> {new}")

        # Create new table with UNIQUE(staff_id)
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {new} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                is_evection BOOLEAN DEFAULT 0,
                UNIQUE (staff_id),
                FOREIGN KEY (staff_id) REFERENCES staffs(id)
            );
        ''')

        # Copy deduplicated data: choose MAX(is_evection) per staff_id
        cur.execute(f'''
            INSERT OR IGNORE INTO {new} (staff_id, is_evection)
            SELECT staff_id, MAX(is_evection) as is_evection
            FROM {day}
            GROUP BY staff_id;
        ''')

        # Replace the old table atomically
        cur.execute(f"DROP TABLE IF EXISTS {day};")
        cur.execute(f"ALTER TABLE {new} RENAME TO {day};")
        conn.commit()

    # Only migrate if original table exists
    for d in ('sat', 'sun'):
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (d,))
        if cur.fetchone():
            migrate_day(d)
        else:
            print(f"Table {d} not found, skipping")

    conn.close()
    print("Migration complete")


if __name__ == '__main__':
    run()
