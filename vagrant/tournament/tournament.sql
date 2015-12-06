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

-- A match may only have one participating player in the case of a bye, so
-- we're splitting the results off into a separate table.
CREATE TABLE match_results (
    match_id integer NOT NULL REFERENCES matches ON DELETE CASCADE,
    player_id integer NOT NULL REFERENCES players ON DELETE CASCADE,
    points_awarded float NOT NULL,
    PRIMARY KEY(match_id, player_id)
);

-- Listing of all players registered for a given tournament
CREATE TABLE tournament_player_maps (
    tourney_id integer NOT NULL REFERENCES tournaments,
    player_id integer NOT NULL REFERENCES players ON DELETE CASCADE,
    -- Changes to False if the player drops from the tournament
    active boolean DEFAULT true NOT NULL,
    -- Changes to True if the player ever receives a bye during
    -- the course of a tournament
    bye_awarded boolean DEFAULT false NOT NULL,
    PRIMARY KEY(tourney_id, player_id)
);


CREATE VIEW player_match_results AS
    SELECT a.tourney_id, a.match_id,
        b.player_id, b.points_awarded
    FROM matches a
        RIGHT JOIN match_results b ON (a.match_id = b.match_id)
    ORDER BY b.player_id
    ;


CREATE VIEW match_win_perc AS
    SELECT tourney_id,
        player_id,
        count(*) as matches_played,
        sum(points_awarded) as total_points,
        sum(points_awarded) / (3 * count(*)) as match_win_perc
    FROM player_match_results
    GROUP BY tourney_id, player_id
    ;


-- Listing of all the opponents a player has had during a given tournament
CREATE VIEW opponents AS
    SELECT DISTINCT tourney_id, player_id, opp_id
    FROM matches c
    RIGHT JOIN (
        SELECT a.match_id, a.player_id, b.player_id as opp_id
        FROM player_match_results a
        LEFT JOIN player_match_results b
        ON a.match_id = b.match_id
        WHERE a.player_id <> b.player_id
        ) d
    ON c.match_id = d.match_id
    ORDER BY player_id, opp_id
    ;




-- Views below this line are still being developed

CREATE VIEW opp_match_win_perc AS
    SELECT a.tourney_id,
        a.player_id,
        a.opp_id,
    FROM opponents a
    LEFT JOIN match_win_perc b
    ON a.opp_id = b.player_id
    ;



 tourney_id | player_id | opp_id | opp_matches_played | opp_total_points | opp_match_win_perc
------------+-----------+--------+--------------------+------------------+--------------------
          1 |         1 |      2 |                  3 |                3 |  0.333333333333333
          1 |         1 |      3 |                  1 |                1 |  0.333333333333333
          1 |         2 |      1 |                  3 |                7 |  0.777777777777778
          1 |         3 |      1 |                  3 |                7 |  0.777777777777778
(4 rows)



