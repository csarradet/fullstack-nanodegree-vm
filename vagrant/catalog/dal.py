import contextlib
import sqlite3

import logging
logger = logging.getLogger(__name__)

from models import User, Category, Item


class AuthSource(object):
    """ Enum listing all authentication sources we currently support. """
    DUMMY = "fake_auth_source"
    GOOGLE_PLUS = "google_plus"
    FACEBOOK = "facebook"


@contextlib.contextmanager
def get_cursor():
    """
    (This function was adapted from the code review for FSND project 2)

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


def model_from_row(model_class, row):
    """
    Converts a database row into a new instance of type model_class.
    Assumes that every column in the row corresponds to a field in
    model_class that has the same spelling and can be copied verbatim.

    Note that this will only work for very simple models; anything
    more complex should have its own converter.

    Throws a TypeError if model_class isn't a class with a no-args constructor.

    Returns a model_class instance if the row was valid, or None if it wasn't.
    """
    if not row:
        return None
    try:
        model = model_class()
        for field in row.keys():
            setattr(model, field, row[field])
        return model
    except KeyError:
        return None


def __simple_get_all(table_name, model_class):
    """
    table_name and model_class will be processed through simple string formatting;
    *do not* send user input to these fields.
    Gets all models of type model_class from the given table.
    """

    output = []
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM {}'.format(table_name))
        result = cursor.fetchall()
    for row in result:
        output.append(model_from_row(model_class, row))
    return output

def __simple_get(table_name, model_class, search_field, search_text):
    """
    search_field, table_name and model_class will be processed through simple string formatting;
    *do not* send user input to these fields.
    Gets a model of type model_class from table_name with the given ID.
    """
    output = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM {} WHERE {} = ?'.format(table_name, search_field), (search_text,))
        output = model_from_row(model_class, cursor.fetchone())
    return output

def __simple_delete(table_name, model_class, search_field, search_text):
    """
    search_field, table_name and model_class will be processed through simple string formatting;
    *do not* send user input to these fields.
    Deletes all models of type model_class from table_name with the given ID.
    """
    with get_cursor() as cursor:
        cursor.execute('DELETE FROM {} WHERE {} = ?'.format(table_name, search_field), (search_text,))


def get_users():
    return __simple_get_all("users", User)

def get_user(user_id):
    return __simple_get("users", User, "user_id", user_id)

def get_or_create_user(username, auth_source, auth_source_id):
    """
    Returns a User instance containing the referenced user's data if it exists
    in the DB, or creates and returns it if it doesn't.

    Assumes that auth_source_id is mandatory, unique, and consistent
    within the domain of a particular auth_source.
    """
    output = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE auth_source = ? AND auth_source_id = ?',
            (auth_source, auth_source_id,))
        output = model_from_row(User, cursor.fetchone())

    if output:
        return output
    else:
        user_id = create_user(username, auth_source, auth_source_id)
        return get_user(user_id)

def create_user(username, auth_source, auth_source_id):
    """ Creates a new database record and returns its ID number. """
    id = None
    with get_cursor() as cursor:
        cursor.execute('INSERT INTO users VALUES (null, ?, ?, ?)', (
            username, auth_source, auth_source_id,))
        cursor.execute('SELECT last_insert_rowid()')
        id = cursor.fetchone()[0]
    return id


def get_categories():
    return __simple_get_all("categories", Category)

def get_category(cat_id):
    return __simple_get("categories", Category, "cat_id", cat_id)

def get_category_by_name(cat_name):
    return __simple_get("categories", Category, "name", cat_name)

def create_category(name, creator_id):
    """ Creates a new category record and returns its ID number. """
    id = None
    with get_cursor() as cursor:
        cursor.execute('INSERT INTO categories VALUES (null, ?, ?)', (
            name, creator_id))
        cursor.execute('SELECT last_insert_rowid()')
        id = cursor.fetchone()[0]
    return id

def delete_category(cat_id):
    __simple_delete("categories", Category, "cat_id", cat_id)


def setup_db():
    """
    Executes our database setup script (this will wipe any existing data).
    Uses a code snippet from http://stackoverflow.com/questions/2380553/sqlite-run-multi-line-sql-script-from-file
    """
    print("Setting up DB")
    print(" - Clearing existing data")
    print(" - Creating tables and views")
    qry = open("catalog.sql", "r").read()
    with get_cursor() as cursor:
        cursor.executescript(qry)
    print(" - Creating dummy records")
    load_dummy_data()
    print("DB setup complete")

def load_dummy_data():
    user1 = get_or_create_user("dummy1@user.com", AuthSource.DUMMY, 1001)
    user2 = get_or_create_user("dummy2@user.com", AuthSource.DUMMY, 2002)

if __name__ == '__main__':
    setup_db()
    load_dummy_data()
