DROP DATABASE IF EXISTS catalog;
CREATE DATABASE catalog;
\c catalog;


-- Create tables --


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email text NOT NULL,
    auth_source text NOT NULL
    );

CREATE TABLE categories (
    cat_id SERIAL PRIMARY KEY,
    name text NOT NULL,
    creator_id integer NOT NULL REFERENCES users
    );

CREATE TABLE items (
    item_id SERIAL PRIMARY KEY,
    name text NOT NULL,
    cat_id integer NOT NULL REFERENCES categories
    creator_id integer NOT NULL REFERENCES users
    );



