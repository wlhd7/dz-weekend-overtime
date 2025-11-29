import sqlite3
from datetime import datetime
from flask import current_app, g
import click


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory=sqlite3.Row
        try:
            # Use WAL to reduce writer contention and set a busy timeout
            g.db.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
        try:
            g.db.execute("PRAGMA busy_timeout=5000;")
        except Exception:
            pass

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_database():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
def init_db_command():
    init_database()
    click.echo('Initialized the database')


sqlite3.register_converter('timestamp', lambda v: datetime.fromisoformat(v.decode()))

def init_db(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
