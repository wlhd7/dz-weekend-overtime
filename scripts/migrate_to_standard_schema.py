#!/usr/bin/env python3
"""Migration script to standardize schema to use department_id and sub_department_id.

This script is idempotent and safe to run multiple times. It will:
- Ensure departments table contains the 8 expected departments (id 1..8).
- Ensure sub_departments table has a department_id column and seed manufacturing sub-departments.
- Add `sub_department_id` column to `staffs` if missing and copy values from `manu_sub_department_id` if present.
- Create helpful indexes.

Run:
  python3 scripts/migrate_to_standard_schema.py instance/weekend-overtime.sqlite

Back up your DB first.
"""
import sqlite3
import sys

DEPARTMENTS = [
    (1, '制造'),
    (2, '品质'),
    (3, '工艺'),
    (4, '装配'),
    (5, '电气'),
    (6, '技术'),
    (7, '机加'),
    (8, '业务'),
]

MANU_SUBDEPTS = [
    (1, '铣床'),
    (2, '车床'),
    (3, 'CNC'),
    (4, '磨床'),
    (5, '线割'),
    (6, '钳工'),
    (7, '生管'),
]


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == column for r in cur.fetchall())


def ensure_departments(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)")
    for id_, name in DEPARTMENTS:
        cur.execute("INSERT OR IGNORE INTO departments (id, name) VALUES (?, ?)", (id_, name))


def ensure_sub_departments_table(cur):
    # ensure table exists with department_id column
    cur.execute("CREATE TABLE IF NOT EXISTS sub_departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)")
    # Add department_id column if missing
    if not column_exists(cur, 'sub_departments', 'department_id'):
        try:
            cur.execute("ALTER TABLE sub_departments ADD COLUMN department_id INTEGER")
        except Exception:
            pass

    # seed manu sub-departments linked to department id 1
    cur.execute('SELECT id FROM departments WHERE name = ?', ('制造',))
    manu_id_row = cur.fetchone()
    manu_id = manu_id_row[0] if manu_id_row else 1
    for idx, name in MANU_SUBDEPTS:
        # insert if not exists for this department
        cur.execute('INSERT OR IGNORE INTO sub_departments (department_id, name) VALUES (?, ?)', (manu_id, name))


def ensure_staffs_subcolumn(cur):
    # add standardized sub_department_id column if missing
    if not column_exists(cur, 'staffs', 'sub_department_id'):
        try:
            cur.execute('ALTER TABLE staffs ADD COLUMN sub_department_id INTEGER')
        except Exception:
            pass

    # if there is a manu_sub_department_id column, copy values into sub_department_id when null
    cur.execute("PRAGMA table_info(staffs)")
    cols = [r[1] for r in cur.fetchall()]
    if 'manu_sub_department_id' in cols:
        cur.execute('UPDATE staffs SET sub_department_id = manu_sub_department_id WHERE sub_department_id IS NULL AND manu_sub_department_id IS NOT NULL')


def create_indexes(cur):
    cur.execute('CREATE INDEX IF NOT EXISTS idx_staffs_dept ON staffs(department_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_staffs_subdept ON staffs(sub_department_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_sub_dept ON sub_departments(department_id)')


def main(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        ensure_departments(cur)
        ensure_sub_departments_table(cur)
        ensure_staffs_subcolumn(cur)
        create_indexes(cur)
        conn.commit()
        print('Migration completed successfully.')
    except Exception as e:
        conn.rollback()
        print('Migration failed:', e)
    finally:
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: migrate_to_standard_schema.py PATH_TO_DB')
        sys.exit(1)
    main(sys.argv[1])
