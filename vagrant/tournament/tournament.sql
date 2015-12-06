-- Initial setup script for the tournament app.
-- Wipes the database if it exists, then creates a
-- new DB and populates it with the required tables.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;


-- **Create tables

-- Listing of all players that have ever registered.
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    name text NOT NULL
);

-- Listing of all tournaments (the top-level entities used
-- to segment our bracketing and reporting).
CREATE TABLE tournaments (
    tourney_id SERIAL PRIMARY KEY
);

-- Listing of all matches (often between two players) and
-- the tournaments in which those matches took place.
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    tourney_id integer NOT NULL REFERENCES tournaments
);

-- Maps the many-to-many relationship between players and the
-- matches they participate in, and also tracks the number of
-- points each player received as a result of a match.
-- Splitting match_results off into its own table allows us to
-- gracefully handle matches that don't have exactly two players
-- (usually because of a bye, but also for group games).
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
    -- Changes to False if the player drops from the tournament.
    -- Inactive players still contribute to tiebreaks, but aren't paired.
    active boolean DEFAULT true NOT NULL,
    -- Changes to True if the player ever receives a bye during
    -- the course of a tournament.
    bye_awarded boolean DEFAULT false NOT NULL,
    PRIMARY KEY(tourney_id, player_id)
);


-- **Create views

-- Convenience view; we'll need both tourney_id and match_id later on
-- when crunching win percentage numbers.
CREATE VIEW player_match_results AS
    SELECT a.tourney_id, a.match_id,
        b.player_id, b.points_awarded
    FROM matches a
        RIGHT JOIN match_results b ON (a.match_id = b.match_id)
    ORDER BY b.player_id
    ;

-- A player's match win percentage during a given tournament
-- (using the DCI's scoring method).
CREATE VIEW match_win_perc AS
    SELECT tourney_id,
        player_id,
        COUNT(*) AS matches_played,
        SUM(points_awarded) AS total_points,
        SUM(points_awarded) / (3 * COUNT(*)) AS match_win_perc
    FROM player_match_results
    GROUP BY tourney_id, player_id
    ;

-- Listing of all the opponents a player has had during a given tournament.
CREATE VIEW opponents AS
    SELECT DISTINCT tourney_id, player_id, opp_id
    FROM matches c
    RIGHT JOIN (
        SELECT a.match_id, a.player_id, b.player_id AS opp_id
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
        a.player_id
    FROM match_win_perc a
    LEFT JOIN (
        SELECT inner.tourney_id,
            inner.player_id,
            SUM(inner.matches_played) as mp_sum,
            SUM(inner.total_points) as point_sum
        FROM match_win_perc inner
        WHERE inner.tourney_id = a.tourney_id
            AND
        ) b

    ;



 tourney_id | player_id | opp_id | opp_matches_played | opp_total_points | opp_match_win_perc
------------+-----------+--------+--------------------+------------------+--------------------
          1 |         1 |      2 |                  3 |                3 |  0.333333333333333
          1 |         1 |      3 |                  1 |                1 |  0.333333333333333
          1 |         2 |      1 |                  3 |                7 |  0.777777777777778
          1 |         3 |      1 |                  3 |                7 |  0.777777777777778
(4 rows)



