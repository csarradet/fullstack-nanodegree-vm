#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
# All user-facing inputs will be scrubbed with bleach before
# being added to the database.
#
# All operations will assume that if a tournament_id is not provided
# the query should be applied to the most recent tourney
# (the one with the largest tourney_id)



#TODO: swiss pairings, player rankings, mwp floor

import psycopg2
import bleach

WIN_POINTS = 3
DRAW_POINTS = 1
LOSE_POINTS = 0

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tourney_id=None):
    """
    Remove all the match records for the given tournament from the database.

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches WHERE tourney_id = %s", (tourney_id,))
    conn.commit()
    conn.close()


def deletePlayers():
    """
    Permanently removes all player records (including the players table).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players")
    conn.commit()
    conn.close()


def removePlayers(tourney_id=None):
    """
    Remove all the player records from the given tournament
    (but not from the players table).

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM tournament_player_maps WHERE tourney_id = %s",
        (tourney_id,))
    conn.commit()
    conn.close()


def deactivatePlayers(tourney_id=None):
    """
    Marks all players in the given tournament as inactive
    (their records will still exist in tournament_player_maps).

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE tournament_player_maps SET active = false " +
            "WHERE tourney_id = %s", (tourney_id,))
    conn.commit()
    conn.close()


def deactivatePlayer(player_id, tourney_id=None):
    """
    As above, but for a single player.
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE tournament_player_maps SET active = false " +
            "WHERE tourney_id = %s AND player_id = %s",
            (tourney_id, player_id))
    conn.commit()
    conn.close()


def countPlayers(tourney_id=None):
    """
    Returns the number of players currently registered.

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tournament_player_maps " +
            "WHERE tourney_id = %s AND active = true", (tourney_id,))
    row_count = c.fetchone()[0]
    conn.commit()
    conn.close()
    return row_count


def registerPlayer(name, tourney_id=None):
    """
    Adds a player to the tournament database and attaches them to the
    given tournament.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
      tourney_id: the id of the currently running tournament
        (use None to auto-detect the most recent one)

    Returns:
        The new player's ID number.
    """
    name = bleach.clean(name)
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players(name) VALUES (%s) RETURNING player_id",(name,))
    player_id = c.fetchone()[0]
    conn.commit()
    conn.close()

    attachPlayer(player_id, tourney_id)
    return player_id

def attachPlayer(player_id, tourney_id=None):
    """
    Attaches an existing player to the given tournament (does not create
    a new record in the players table).

    Args:
        player_id: The id of the player to be added
        tourney_id = The id of the tournament to which they should be attached.
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO tournament_player_maps(tourney_id, player_id) " +
        "VALUES (%s, %s)", (tourney_id, player_id,))
    conn.commit()
    conn.close()


def playerStandings(tourney_id=None):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT player_id, name, total_points, matches_played " +
        "FROM player_standings " +
        "WHERE tourney_id = %s AND active = true", (tourney_id,))
    output = []
    for result in c:
        # 3 points == 1 match win; doing a conversion here so that
        # the test cases will see a win count in the format they expect
        points = result[2] or 0
        matches = result[3] or 0
        output.append((result[0], result[1], float(points)/3, matches))
    conn.commit()
    conn.close()

    return output

def reportMatch(winner, loser, tourney_id=None):
    """Records the outcome of a single match between two players.

    Args:
        winner:  the id number of the player who won
        loser:  the id number of the player who lost
        draw: if true, both players should receive a draw result
            instead of a win and loss, respectively
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO matches(tourney_id) VALUES(%s) RETURNING match_id", (tourney_id,))
    match_id = c.fetchone()[0]
    c.execute("INSERT INTO match_results(match_id, player_id, points_awarded) " +
            "VALUES(%s, %s, %s)", (match_id, winner, WIN_POINTS))
    c.execute("INSERT INTO match_results(match_id, player_id, points_awarded) " +
            "VALUES(%s, %s, %s)", (match_id, loser, LOSE_POINTS))
    conn.commit()
    conn.close()


def reportDraw(player1, player2, tourney_id=None):
    """
    Reports that the game played between these two players was a draw.

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO matches(tourney_id) VALUES(%s) RETURNING match_id", (tourney_id,))
    match_id = c.fetchone()[0]
    c.execute("INSERT INTO match_results(match_id, player_id, points_awarded) " +
            "VALUES(%s, %s, %s)", (match_id, player1, DRAW_POINTS))
    c.execute("INSERT INTO match_results(match_id, player_id, points_awarded) " +
            "VALUES(%s, %s, %s)", (match_id, player2, DRAW_POINTS))
    conn.commit()
    conn.close()


def reportBye(player, tourney_id=None):
    """
    Reports that the player received a bye, and updates the database so
    that they will be ineligible for further byes.

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO matches(tourney_id) VALUES(%s) RETURNING match_id", (tourney_id,))
    match_id = c.fetchone()[0]
    c.execute("INSERT INTO match_results(match_id, player_id, points_awarded) " +
            "VALUES(%s, %s, %s)", (match_id, player, WIN_POINTS))
    c.execute("UPDATE tournament_player_maps SET bye_awarded = true " +
            "WHERE tourney_id = %s and player_id = %s", (tourney_id, player,))
    conn.commit()
    conn.close()


def swissPairings(tourney_id=None):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    bye_player_id = calculateBye(tourney_id)

    player_list = []
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT player_id, name FROM player_standings " +
        "WHERE tourney_id = %s AND active = true",
        (tourney_id,))
    for result in c:
        if result[0] == bye_player_id:
            reportBye(bye_player_id, tourney_id)
        else:
            player_list.append((result[0], result[1]))
    conn.commit()
    conn.close()

    output = []
    opponent = None
    for player in player_list:
        if opponent == None:
            opponent = player
        else:
            output.append((player[0], player[1], opponent[0], opponent[1]))
            opponent = None
    return output


def calculateBye(tourney_id=None):
    """
    If the current tournament has an odd number of active players,
    returns the ID of the lowest-ranked player who has yet to receive
    a bye.
    Otherwise, returns None
    """
    if not tourney_id:
        tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM player_standings " +
        "WHERE tourney_id = %s AND active = true", (tourney_id,))
    count = c.fetchone()[0]
    conn.commit()
    conn.close()

    if count % 2 == 0:
        return None

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT player_id FROM player_standings_asc " +
        "WHERE tourney_id = %s AND bye_awarded = false AND active = true " +
        "LIMIT 1", (tourney_id,))
    bye_player_id = c.fetchone()[0]
    conn.commit()
    conn.close()

    return bye_player_id


def getOrCreateTournament():
    """
    If there are any tournaments in the database, return the tourney_id
    of the most recently created one.
    Otherwise, create a new tournament and return its tourney_id.
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT tourney_id FROM tournaments ORDER BY tourney_id DESC LIMIT 1")
    found = c.fetchone()
    conn.commit()
    conn.close()
    if found:
        return found[0]
    else:
        return createTournament()


def createTournament():
    """
    Add a new tournament to the database and return its tourney_id.
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO tournaments(tourney_id) VALUES(default) RETURNING tourney_id")
    tourney_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return tourney_id

