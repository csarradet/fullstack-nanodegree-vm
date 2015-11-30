-- Initial setup script for the tournament app.
-- Wipes the database if it exists, then creates a
-- new DB and populates it with the required tables.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;


-- Listing of all players that have ever registered
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE tournaments (
    tourney_id SERIAL PRIMARY KEY
);

CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    tourney_id integer NOT NULL REFERENCES tournaments
);

-- A match may only have one player in the case of a bye, so
-- we're splitting that off into a separate table.
CREATE TABLE match_results (
    match_id integer NOT NULL REFERENCES matches,
    player_id integer NOT NULL REFERENCES players,
    points_awarded integer NOT NULL,
    PRIMARY KEY(match_id, player_id)
);

-- Listing of all players registered for a given tournament
CREATE TABLE tournament_player_maps (
    tourney_id integer NOT NULL REFERENCES tournaments,
    player_id integer NOT NULL REFERENCES players,
    -- Changes to False if the player drops from the tournament
    active boolean DEFAULT true NOT NULL,
    -- Changes to True if the player ever receives a bye during
    -- the course of a tournament
    bye_awarded boolean DEFAULT false NOT NULL,
    PRIMARY KEY(tourney_id, player_id)
);


