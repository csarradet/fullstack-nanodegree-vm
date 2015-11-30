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



import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteMatches(tourney_id=None):
    """
    Remove all the match records from the database.

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """


def deletePlayers(tourney_id=None):
    """
    Remove all the player records from the given tournament.

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """
    conn=connect()
    c=conn.cursor()
    c.execute("INSERT INTO players(name) VALUES (%s) RETURNING player_id",(name,))
    player_id = c.fetchone()[0]
    conn.commit()
    conn.close()

def countPlayers(tourney_id=None):
    """
    Returns the number of players currently registered.

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """


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
    """
    name = bleach.clean(name)
    tourney_id = getOrCreateTournament()

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players(name) VALUES (%s) RETURNING player_id",(name,))
    player_id = c.fetchone()[0]
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

def reportDraw(player1, player2, tourney_id=None):
    """
    Reports that the provided lay

    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """

def reportBye(player, tourney_id=None):
    """
    Args:
        tourney_id: the id of the currently running tournament
          (use None to auto-detect the most recent one)
    """

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

