"""
This file houses our data abstraction layer.  It insulates the rest
of the application code from whichever database we happen to be
using (sqlite3, in this case) and handles things like caching.

Note that while the __simple_xxx functions use unsafe string
concatenation for table and column names, they're only intended
to be used from within this module and are always called with static values.
All data originating from the user (things like names and ID numbers)
are properly passed to the DB using parameterized queries.

(Side note: while the intro lessons for this project used SQLAlchemy,
    I have some philosophical issues with ORM.  Absent the need to support
    multiple DB types, I prefer to have the database code under my
    control in its own module.)
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
    conn = sqlite3.connect("data source=catalog.db; foreign keys=true;")
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

def __simple_get_all(UNSAFE_table_name, UNSAFE_entity_class):
    """
    UNSAFE fields may be processed through simple string formatting;
    *do not* send user input to these fields.

    Gets all entities of type entity_class from the given table.
    """
    output = []
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM {}'.format(UNSAFE_table_name))
        result = cursor.fetchall()
    for row in result:
        output.append(entity_from_row(UNSAFE_entity_class, row))
    return output

def __simple_get(UNSAFE_table_name, UNSAFE_entity_class, UNSAFE_search_field, search_text):
    """
    UNSAFE fields may be processed through simple string formatting;
    *do not* send user input to these fields.

    Gets the first entity of type entity_class from table_name whose data in
    column search_field matches search_text.
    """
    output = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM {} WHERE {} = ? LIMIT 1'.format(
            UNSAFE_table_name, UNSAFE_search_field), (search_text,))
        output = entity_from_row(UNSAFE_entity_class, cursor.fetchone())
    return output

def __simple_delete(UNSAFE_table_name, UNSAFE_entity_class, UNSAFE_search_field, search_text):
    """
    UNSAFE fields may be processed through simple string formatting;
    *do not* send user input to these fields.

    Deletes all entities of type entity_class from table_name whose data in
    column search_field matches search_text.
    """
    with get_cursor() as cursor:
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute('DELETE FROM {} WHERE {} = ?'.format(
            UNSAFE_table_name, UNSAFE_search_field), (search_text,))



def get_users():
    """ Returns a list of all users who have ever logged in. """
    return __simple_get_all("users", User)

def get_user(user_id):
    """
    Returns a User instance if the user_id corresponds to someone who has
    logged in before, or None if it doesn't.
    """
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
    """ Get a list of all categories that currently exist. """
    return __simple_get_all("pretty_categories", Category)

def get_category(cat_id):
    """ Get a particular category if it exists, or None if it doesn't. """
    return __simple_get("pretty_categories", Category, "cat_id", cat_id)

def get_category_by_name(cat_name):
    """ Get a particular category if it exists, or None if it doesn't. """
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
    """ Delete a particular category if it exists. """
    __simple_delete("categories", Category, "cat_id", cat_id)

def update_category(cat_id, name):
    """ Update the DB record for a particular category. """
    with get_cursor() as cursor:
        cursor.execute('UPDATE categories SET name=? WHERE cat_id=?', (name, cat_id))



def get_items():
    """ Get a list of all items that exist. """
    return __simple_get_all("pretty_items", Item)

def get_item(item_id):
    """ Get a particular item if it exists, or None if it doesn't. """
    return __simple_get("pretty_items", Item, "item_id", item_id)

def get_items_by_cat(cat_id, lightweight=False):
    """
    Get a list of all items that belong to a particular category.
    If lightweight, some bulky information like binary picture data
    may be missing from the item instances.
    """
    output = []
    with get_cursor() as cursor:
        if lightweight:
            cursor.execute('SELECT * FROM pretty_items_light WHERE cat_id = ?', (cat_id,))
        else:
            cursor.execute('SELECT * FROM pretty_items WHERE cat_id = ?', (cat_id,))
        result = cursor.fetchall()
    for row in result:
        output.append(entity_from_row(Item, row))
    return output

def get_item_by_name(cat_id, item_name):
    """ Get a particular item if it exists, or None if it doesn't. """
    output = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM pretty_items WHERE cat_id = ? AND name = ?',
            (cat_id, item_name,))
        output = entity_from_row(Item, cursor.fetchone())
    return output

def get_recent_items(count):
    """ Get a list of the <count> most recent items that have been created or changed. """
    output = []
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM pretty_items ORDER BY changed DESC LIMIT ?', (count,))
        result = cursor.fetchall()
    for row in result:
        output.append(entity_from_row(Item, row))
    return output

def list_items_by_cat():
    """
    Returns a list of sorted tuples:
        Item 0: A category instance
        Item 1: An array containing all item instances in that category
    This is used to build the dashboard sidebar; in production, a
    caching solution or AJAX would be tacked on for performance reasons.
    """
    output = []
    for cat in get_categories():
        items = get_items_by_cat(cat.cat_id, lightweight=True)
        output.append((cat, items))
    return output

def create_item(name, category_id, creator_id, pic, description=None):
    """ Creates a new Item instance and returns its item_id. """
    id = None
    if description is None:
        description = "Placeholder item description"
    with get_cursor() as cursor:
        # First, create the picture and get its new ID number
        cursor.execute("INSERT INTO pictures VALUES (null, ?)",
            (sqlite3.Binary(pic),))
        cursor.execute('SELECT last_insert_rowid()')
        pic_id = cursor.fetchone()[0]

        # Now create the actual item and return its ID
        cursor.execute("INSERT INTO items VALUES (null,?,?,?,?,?,(DATETIME('now')))",
            (name, description, pic_id, category_id, creator_id))
        cursor.execute('SELECT last_insert_rowid()')
        id = cursor.fetchone()[0]
    return id

def delete_item(item_id):
    """ Deletes a particular item. """
    __simple_delete("items", Item, "item_id", item_id)

def update_item(item_id, name=None, description=None, pic_id=None, pic=None, cat_id=None):
    """
    Selectively updates the DB fields for a particular item.  Any fields that are left as
    None will retain their existing values.

    If pic (binary picture data) is not none, a pic_id must also be provided.
    """

    # It would probably be more efficient to smash everything into a single SQL statement;
    # going to keep it simple for this project though.  Item updates should be fairly
    # uncommon anyway.
    with get_cursor() as cursor:
        if name is not None:
            cursor.execute("UPDATE items SET name=? WHERE item_id=?", (name, item_id))

        if description is not None:
            cursor.execute("UPDATE items SET description=? WHERE item_id=?", (description, item_id))

        if pic is not None:
            if pic_id is None:
                raise ValueError("Received updated picture data, but no pic_id")
            cursor.execute("UPDATE pictures SET pic=? WHERE pic_id=?", (sqlite3.Binary(pic), pic_id))

        if cat_id is not None:
            cursor.execute("UPDATE items SET cat_id=? WHERE item_id=?", (cat_id, item_id))

        cursor.execute("UPDATE items SET changed=DATETIME('now') WHERE item_id=?", (item_id,))



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

def load_dummy_data():
    """
    Creates a few dummy values to help with debugging.
    """
    user1 = get_or_create_user("dummy1@user.com", AuthSource.DUMMY, 1001).user_id
    user2 = get_or_create_user("dummy2@user.com", AuthSource.DUMMY, 2002).user_id
    cat1 = create_category("Food", user1)
    cat2 = create_category("Explosives", user2)
    # Just a dummy base64-encoded JPEG file
    pic = "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"
    item1_1 = create_item("Gagh", cat1, user1, pic, "Very fresh")
    item1_2 = create_item("Roasted Tauntaun", cat1, user2, pic, "Also smells bad on the inside")
    item2_1 = create_item("Red Matter", cat2, user1, pic, "For destroying planets")
    item2_2 = create_item("Thermal Detonator", cat2, user2, pic, "For destroying buildings")



if __name__ == '__main__':
    print("Setting up DB")
    initial_db_setup()
    print("Creating dummy records")
    load_dummy_data()
