-- Enforce foreign key constraints --
PRAGMA foreign_keys=ON;

-- Wipe any existing data --
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;


-- Create tables --
CREATE TABLE users (
    -- The user's unique ID within our own system
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    auth_source TEXT NOT NULL,
    -- The user's unique ID, as reported by the auth source
    auth_source_id TEXT NOT NULL
    );

CREATE TABLE categories (
    cat_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    FOREIGN KEY(creator_id) REFERENCES users(user_id)
    );

CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cat_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    created DATETIME NOT NULL,
    FOREIGN KEY(cat_id) REFERENCES categories(cat_id),
    FOREIGN KEY(creator_id) REFERENCES users(user_id)
    );



