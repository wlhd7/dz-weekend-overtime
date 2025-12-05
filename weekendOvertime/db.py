import sqlite3
from datetime import datetime
from flask import current_app, g
import click


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
                #
                current_app.config['DATABASE'],
                #
                detect_types=sqlite3.PARSE_DECLTYPES
            )
        #
        g.db.row_factory=sqlite3.Row
        try:
            # Use WAL to reduce writer contention and set a busy timeout
            # what is WAL?
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


"""Database helpers for the weekendOvertime Flask app.

This module provides a small set of utilities for working with the
SQLite database used by the application. If you're new to Flask these
are the main concepts used here:

- `current_app`: proxy to the Flask application instance.
- `g`: a request-scoped namespace for storing objects (like a DB
  connection) for the lifetime of a request.
- `teardown_appcontext`: registers a function to run after each
  request to clean up resources (like closing a DB connection).

The functions below lazily open a SQLite connection (on first use in a
request), close it at the end of the request, and provide a small
helper to initialize the database schema from `schema.sql`.
"""

import sqlite3
from datetime import datetime
from flask import current_app, g
import click


def get_db() -> sqlite3.Connection:
    """Return a SQLite `Connection` for the current request.

    The connection is created once per request and stored on `flask.g` so
    subsequent calls during the same request reuse the same object.

    Key options used when creating the connection:
    - `detect_types=sqlite3.PARSE_DECLTYPES`: allows SQLite to return
      Python objects for declared column types when a converter is
      registered (see `register_converter` below).
    - `row_factory = sqlite3.Row`: makes cursor fetches return rows
      that behave like dicts (access columns by name).

    We also set two PRAGMA options that help when multiple writes may
    occur in quick succession:
    - `journal_mode=WAL`: Write-Ahead Logging improves concurrency for
      readers/writers compared to the default rollback journal.
    - `busy_timeout=5000`: tells SQLite to wait up to 5000ms for a
      locked database rather than raising `sqlite3.OperationalError`
      immediately.
    """

    if 'db' not in g:
        # Lazy-create the connection and attach to `g` for request scope.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )

        # Return rows as dictionary-like objects (access columns by name).
        g.db.row_factory = sqlite3.Row

        # Attempt to set WAL journal mode. If the PRAGMA fails for any
        # reason we swallow the exception: the app will still work with
        # the default journal mode, but WAL is preferred for concurrency.
        try:
            g.db.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass

        # Ask SQLite to wait a short while when the DB is locked instead
        # of failing immediately. This helps when many clients perform
        # writes in rapid succession.
        try:
            g.db.execute("PRAGMA busy_timeout=5000;")
        except Exception:
            pass

    return g.db


def close_db(e=None):
    """Close the database connection for the current request.

    This is intended to be registered with Flask's
    `teardown_appcontext` so it runs automatically after each request.
    """

    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_database():
    """Initialize the database from the `schema.sql` file.

    This opens the app's configured database and executes the SQL
    statements in `schema.sql`. Use the included `init-db` Click
    command (registered below) to call this from the command line:

        flask init-db
    """

    db = get_db()

    # `open_resource` reads files relative to the application package.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
def init_db_command():
    """CLI command to initialize the database.

    The command is registered on the Flask app so you can run it with
    `flask init-db` while the application environment is configured.
    """

    init_database()
    click.echo('Initialized the database')


# Register a converter so SQLite values declared as `timestamp` are
# converted to Python `datetime` objects when rows are fetched. The
# converter receives the raw bytes from SQLite, so we decode and parse
# them using `datetime.fromisoformat` which matches the serializer used
# when writing timestamps in ISO format.
sqlite3.register_converter('timestamp', lambda v: datetime.fromisoformat(v.decode()))


def init_db(app):
    """Register database helpers on the given Flask `app`.

    This function wires the `close_db` teardown handler so connections
    are closed after each request and also registers the `init-db`
    Click command on the application's CLI.
    """

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)