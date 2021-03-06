-- Initial setup script for the tournament app.
-- Wipes the database if it exists, then creates a
-- new DB and populates it with the required tables/views.

-- The ON DELETE CASCADE bits are only here to make the
-- test code simpler; in production, they would be replaced
-- with more robust safety measures in the application code.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;


-- Create tables --

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
    tourney_id integer NOT NULL REFERENCES tournaments ON DELETE CASCADE
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
    tourney_id integer NOT NULL REFERENCES tournaments ON DELETE CASCADE,
    player_id integer NOT NULL REFERENCES players ON DELETE CASCADE,
    -- Changes to False if the player drops from the tournament.
    -- Inactive players still contribute to tiebreaks, but aren't paired.
    active boolean DEFAULT true NOT NULL,
    -- Changes to True if the player ever receives a bye during
    -- the course of a tournament.
    bye_awarded boolean DEFAULT false NOT NULL,
    PRIMARY KEY(tourney_id, player_id)
    );


-- Create views --

-- Just for convenience; we'll need both tourney_id and match_id later on
-- when crunching win percentage numbers.
CREATE VIEW player_match_results AS
    SELECT a.tourney_id, a.match_id,
        b.player_id, b.points_awarded
    FROM matches a
        RIGHT JOIN match_results b ON (a.match_id = b.match_id)
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

-- Listing of all the opponents a player has been matched with
-- during a given tournament.
CREATE VIEW opponents AS
    SELECT DISTINCT tourney_id, player_id, opp_id
    FROM matches c
    RIGHT JOIN (
        SELECT a.match_id,
            a.player_id,
            b.player_id AS opp_id
        FROM player_match_results a
        LEFT JOIN player_match_results b
        ON a.match_id = b.match_id
        WHERE a.player_id <> b.player_id
        ) d
    ON c.match_id = d.match_id
    ;

-- Helper to clean up the next view, shows raw match stats for
-- all opponents
CREATE VIEW omw_subquery AS
    SELECT a.tourney_id, a.player_id, a.opp_id,
        b.matches_played, b.total_points
    FROM opponents a
    LEFT JOIN match_win_perc b
    ON a.opp_id = b.player_id
    WHERE a.tourney_id = b.tourney_id
    ;

-- The aggregate match win percentage of a player's opponents during
-- a given tournament (using the DCI's scoring method)
CREATE VIEW opp_match_win_perc AS
    SELECT a.tourney_id,
        a.player_id,
        SUM(a.matches_played) as all_opps_matches_played,
        SUM(a.total_points) as all_opps_total_points,
        SUM(a.total_points) / (3 * SUM(a.matches_played))
            AS all_opps_match_win_perc
    FROM omw_subquery a
    GROUP BY a.tourney_id, a.player_id
    ;

-- Most tournament pairing code will use this view.
-- Contains all fields needed to list the current tournament standings
CREATE VIEW player_standings AS
    SELECT a.tourney_id,
        a.player_id,
        a.active,
        a.bye_awarded,
        b.matches_played,
        b.total_points,
        c.all_opps_match_win_perc,
        d.name
    FROM tournament_player_maps a
        LEFT JOIN match_win_perc b
            ON a.player_id = b.player_id
            AND a.tourney_id = b.tourney_id
        LEFT JOIN opp_match_win_perc c
            ON a.player_id = c.player_id
            AND a.tourney_id = c.tourney_id
        LEFT JOIN players d ON a.player_id = d.player_id
    ORDER BY a.tourney_id,
        b.total_points DESC NULLS LAST,
        c.all_opps_match_win_perc DESC NULLS LAST,
        a.player_id
    ;

-- Same as above with reversed sorting.  Only used to calculate byes
CREATE VIEW player_standings_asc AS
    SELECT a.tourney_id,
        a.player_id,
        a.active,
        a.bye_awarded,
        b.matches_played,
        b.total_points,
        c.all_opps_match_win_perc,
        d.name
    FROM tournament_player_maps a
        LEFT JOIN match_win_perc b
            ON a.player_id = b.player_id
            AND a.tourney_id = b.tourney_id
        LEFT JOIN opp_match_win_perc c
            ON a.player_id = c.player_id
            AND a.tourney_id = c.tourney_id
        LEFT JOIN players d ON a.player_id = d.player_id
    ORDER BY a.tourney_id,
        b.total_points NULLS FIRST,
        c.all_opps_match_win_perc NULLS FIRST,
        a.player_id DESC
    ;
