import contextlib
import sqlite3

import logging
logger = logging.getLogger(__name__)

from models import User

# Parameterized call syntax:
# c.execute("DELETE FROM matches WHERE tourney_id = %s", (tourney_id,))

@contextlib.contextmanager
def get_cursor():
    """
    (This function was taken from the code review for FSND project 2)

    Helper function that provides a DB cursor scoped to a with block.

    Sample call:
        with with_cursor() as cursor:
            cursor.execute("delete from matches;")
    """
    conn = sqlite3.connect("catalog.db")
    # This wrapper adds the ability to access a row's fields by column name,
    # allowing us to auto-convert them to entities as long as the field names
    # match (see model_from_row()).
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        yield c
    except:
        raise
    else:
        conn.commit()
    finally:
        conn.close()


def setup_db():
    """
    Executes our database setup script (this will wipe any existing data).
    Uses a code snippet from http://stackoverflow.com/questions/2380553/sqlite-run-multi-line-sql-script-from-file
    """
    print("Setting up DB")
    print(" - Creating tables and views")
    qry = open("catalog.sql", "r").read()
    with get_cursor() as cursor:
        cursor.executescript(qry)
    print(" - Creating dummy records")
    load_dummy_data()
    print("DB setup complete")


def load_dummy_data():
    with get_cursor() as cursor:
        cursor.execute('INSERT INTO users VALUES (null, "dummy1@user.com", "fake_auth_source")')
        cursor.execute('INSERT INTO users VALUES (null, "dummy2@user.com", "fake_auth_source")')


def model_from_row(model_class, row):
    """
    Converts a database row into a new instance of type model_class.
    Assumes that every column in the row corresponds to a field in
    model_class that has the same spelling and can be copied verbatim.

    Note that this will only work for very simple models; anything
    more complex should have its own converter.
    """
    model = model_class()
    for field in row.keys():
        setattr(model, field, row[field])
    return model


def get_users():
    output = []
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM users')
        result = cursor.fetchall()
    for row in result:
        output.append(model_from_row(User, row))
    return output

def get_user(user_id):
    output = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        output = model_from_row(User, cursor.fetchone())
    return output



