-- Enforce foreign key constraints --
-- (Note that we use cascading deletes below -- this is just
--  to make the project code simpler.  In production more
--  robust controls would be added to the business logic
--  layer instead.)
PRAGMA foreign_keys=ON;

-- Wipe any existing data --
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS pictures;
DROP VIEW IF EXISTS pretty_categories;
DROP VIEW IF EXISTS pretty_items;
DROP VIEW IF EXISTS pretty_items_light;

-- Create tables --
CREATE TABLE users (
    -- The user's unique ID within our own system
    user_id INTEGER PRIMARY KEY,
    -- The user's name as displayed by their auth source (e.g. user@example.com)
    username TEXT NOT NULL,
    -- The service through which this user authenticates (facebook, google+, etc)
    auth_source TEXT NOT NULL,
    -- The user's unique ID, as reported by the auth source
    auth_source_id TEXT NOT NULL
    );

CREATE TABLE categories (
    cat_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    -- The user that owns this category
    creator_id INTEGER NOT NULL,
    FOREIGN KEY(creator_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    -- The stored picture that matches this item
    pic_id INTEGER NOT NULL,
    -- The category to which this item belongs
    cat_id INTEGER NOT NULL,
    -- The user that owns this item
    creator_id INTEGER NOT NULL,
    -- The last time this object was created or modified
    changed DATETIME NOT NULL,
    FOREIGN KEY(cat_id) REFERENCES categories(cat_id) ON DELETE CASCADE,
    FOREIGN KEY(creator_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(pic_id) REFERENCES pictures(pic_id) ON DELETE CASCADE
    );

-- SQLite has trouble operating on rows that contain large blobs,
-- moving pictures into their own table as a workaround.
-- 1:1 mapping between items and pictures in this implementation,
-- but it would be possible to add in caching if many users were
-- expected to share the same image.
CREATE TABLE pictures (
    pic_id INTEGER PRIMARY KEY,
    --Binary JPEG data, base64 encoded
    pic BLOB NOT NULL
    );



-- Create views --
-- These are used by the DAL to pull all related info on an item/cat with a single query
CREATE VIEW pretty_categories AS
    SELECT c.cat_id, c.name, c.creator_id,
        u.username AS creator_name
    FROM categories AS c JOIN users AS u ON (c.creator_id = u.user_id)
    ;

CREATE VIEW pretty_items AS
    SELECT i.item_id, i.name, i.description, i.pic_id, i.cat_id, i.creator_id, i.changed,
        u.username AS creator_name,
        c.name AS cat_name,
        p.pic
    FROM items AS i
        JOIN users AS u ON (i.creator_id = u.user_id)
        JOIN categories AS c ON (i.cat_id = c.cat_id)
        JOIN pictures AS p ON (i.pic_id = p.pic_id)
    ;

-- Same as above, but without the picture payloads
-- (Primarily used to build sidebar menus, where the extra overhead
--  was causing load time problems)
CREATE VIEW pretty_items_light AS
    SELECT i.item_id, i.name, i.description, i.pic_id, i.cat_id, i.creator_id, i.changed,
        u.username AS creator_name,
        c.name AS cat_name
    FROM items AS i
        JOIN users AS u ON (i.creator_id = u.user_id)
        JOIN categories AS c ON (i.cat_id = c.cat_id)
    ;
