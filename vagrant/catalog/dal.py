"""
This file houses our data abstraction layer.  It insulates the rest
of the application code from whichever database we happen to be
using (sqlite3, in this case).

Note that while the __simple_xxx functions use unsafe string
concatenation for table and column names, they're only intended
to be used from within this module and are always called with static values.
All data originating from the user (things like names and ID numbers)
are properly passed to the DB using parameterized queries.

***
The example classes for this project used SQLAlchemy's ORM solution --
not to start a flame war, but I have some philosophical issues with
ORM as a whole.
Given the choice, I'd much rather have the database code under my
control in its own module.
***
"""

import contextlib
import sqlite3

import logging
logger = logging.getLogger(__name__)

from entities import AuthSource, User, Category, Item


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
    # This Row wrapper adds the ability to access a row's fields by column name,
    # allowing us to auto-convert them to entities as long as the field names
    # match (see entity_from_row()).
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

def entity_from_row(entity_class, row):
    """
    Converts a database row into a new instance of type entity_class.
    Assumes that every column in the row corresponds to a field in
    entity_class that has the same spelling and can be copied verbatim.

    Note that this will only work for very simple entities; anything
    more complex should have its own converter.

    Throws a TypeError if entity_class isn't a class with a no-args constructor.

    Returns an entity_class instance if the row was valid, or None if it wasn't.
    """
    if not row:
        return None
    try:
        entity = entity_class()
        for field in row.keys():
            setattr(entity, field, row[field])
        return entity
    except KeyError:
        return None

def __simple_get_all(table_name, entity_class):
    """
    table_name and entity_class will be processed through simple string formatting;
    *do not* send user input to these fields.
    Gets all entities of type entity_class from the given table.
    """
    output = []
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM {}'.format(table_name))
        result = cursor.fetchall()
    for row in result:
        output.append(entity_from_row(entity_class, row))
    return output

def __simple_get(table_name, entity_class, search_field, search_text):
    """
    search_field, table_name and entity_class will be processed through simple string formatting;
    *do not* send user input to these fields.
    Gets the first entity of type entity_class from table_name with the given ID.
    """
    output = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM {} WHERE {} = ? LIMIT 1'.format(table_name, search_field), (search_text,))
        output = entity_from_row(entity_class, cursor.fetchone())
    return output

def __simple_delete(table_name, entity_class, search_field, search_text):
    """
    search_field, table_name and entity_class will be processed through simple string formatting;
    *do not* send user input to these fields.
    Deletes all entities of type entity_class from table_name with the given ID.
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
        output = entity_from_row(User, cursor.fetchone())

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
    return __simple_get_all("pretty_categories", Category)

def get_category(cat_id):
    return __simple_get("pretty_categories", Category, "cat_id", cat_id)

def get_category_by_name(cat_name):
    return __simple_get("pretty_categories", Category, "name", cat_name)

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



def get_items():
    return __simple_get_all("pretty_items", Item)

def get_item(item_id):
    return __simple_get("pretty_items", Item, "item_id", item_id)

def get_items_by_cat(cat_id):
    output = []
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM pretty_items WHERE cat_id = ?', (cat_id,))
        result = cursor.fetchall()
    for row in result:
        output.append(entity_from_row(Item, row))
    return output

def get_item_by_name(cat_id, item_name):
    output = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM pretty_items WHERE cat_id = ? AND name = ?',
            (cat_id, item_name,))
        output = entity_from_row(Item, cursor.fetchone())
    return output

def create_item(name, category_id, creator_id, description=None):
    id = None
    if description is None:
        description = "Placeholder item description"
    with get_cursor() as cursor:
        cursor.execute("INSERT INTO items VALUES (null, ?, ?, ?, ?, (DATETIME('now')))", (
            name, description, category_id, creator_id))
        cursor.execute('SELECT last_insert_rowid()')
        id = cursor.fetchone()[0]
    return id

def delete_item(item_id):
    __simple_delete("items", Item, "item_id", item_id)

def get_recent_items(count):
    output = []
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM pretty_items ORDER BY changed DESC LIMIT ?', (count,))
        result = cursor.fetchall()
    for row in result:
        output.append(entity_from_row(Item, row))
    return output



def initial_db_setup():
    """
    Executes our database setup script (this will wipe any existing data).
    Uses a code snippet from http://stackoverflow.com/questions/2380553/sqlite-run-multi-line-sql-script-from-file
    """
    print(" - Clearing existing data")
    print(" - Creating tables and views")
    qry = open("catalog.sql", "r").read()
    with get_cursor() as cursor:
        cursor.executescript(qry)
    print(" - DB initial setup complete")

def session_setup():
    """
    Call once when spinning up an app instance.
    Runs any code required to prepare the DB for activity
    (just enabling foreign keys as per SQLite requirements, in this case).
    """
    with get_cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = ON;")
    print(" - DB session setup complete")

def load_dummy_data():
    """
    Creates a few dummy values to help with debugging.
    """
    user1 = get_or_create_user("dummy1@user.com", AuthSource.DUMMY, 1001).user_id
    user2 = get_or_create_user("dummy2@user.com", AuthSource.DUMMY, 2002).user_id
    cat1 = create_category("Food", user1)
    cat2 = create_category("Explosives", user2)
    item1_1 = create_item("Gagh", cat1, user1, "Very fresh")
    item1_2 = create_item("Roasted Tauntaun", cat1, user2, "Also smells bad on the inside")
    item2_1 = create_item("Red Matter", cat2, user1, "For destroying planets")
    item2_2 = create_item("Thermal Detonator", cat2, user2, "For destroying buildings")



if __name__ == '__main__':
    print("Setting up DB")
    initial_db_setup()
    print("Creating dummy records")
    load_dummy_data()
