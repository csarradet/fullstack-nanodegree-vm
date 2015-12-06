#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    wipeDatabase()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    wipeDatabase()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    wipeDatabase()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    wipeDatabase()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    wipeDatabase()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    wipeDatabase()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


# If there is an odd number of players, award a bye
# (also tests deactivating players)
def testByes():
    wipeDatabase()
    id1 = registerPlayer("Ramza")
    id2 = registerPlayer("Agrias")
    id3 = registerPlayer("Delita")
    id4 = registerPlayer("Gafgarion")
    oldCount = countPlayers()
    pairings = swissPairings()
    standings = playerStandings()
    if standings[0][2] != 0:
        raise ValueError(
            "For four players, no one should receive a bye")

    deactivatePlayer(id4)
    newCount = countPlayers()
    if oldCount - newCount != 1:
        raise ValueError(
            "Player count should be reduced by one after deactivating")

    pairings = swissPairings()
    standings = playerStandings()
    if standings[0][2] == 0:
        raise ValueError(
            "For three players, exactly one should receive a bye")
    print "9. Byes are being awarded (only) when player count is odd"


# Support matches that result in a draw
def testDraws():
    wipeDatabase()
    id1 = registerPlayer("Pacquiao")
    id2 = registerPlayer("Marquez")
    reportDraw(id1, id2)
    for record in playerStandings():
        if record[2] != (1.0/3.0):
            raise ValueError(
                "Both players should have one match win point after " +
                "a draw (found {}, expected 0.333...)".format(record[2]))
    print "10. Draws are being awarded correctly"


# Support tiebreaks via Opponent Match Win (OMW) percentage
def testTiebreaks():
    wipeDatabase()
    id1 = registerPlayer("Saber")
    id2 = registerPlayer("Lancer")
    id3 = registerPlayer("Assassin")
    id4 = registerPlayer("Rider")
    reportMatch(id1, id3)
    reportMatch(id2, id4)
    reportMatch(id1, id2)

    curr_rank = 1
    ranks = {}
    for record in playerStandings():
        ranks[record[0]] = curr_rank
        curr_rank += 1
    if ranks[id3] > ranks[id4]:
        raise ValueError(
            "When match points are tied, opponent match win " +
            "percentage should be used as a tiebreaker " +
            "({} < {})".format(ranks[id3], ranks[id4]))

    # Reversing the results to ensure that wasn't a fluke
    reportMatch(id2, id1)
    reportMatch(id2, id1)
    curr_rank = 1
    ranks = {}
    for record in playerStandings():
        ranks[record[0]] = curr_rank
        curr_rank += 1
    if ranks[id3] < ranks[id4]:
        raise ValueError(
            "When match points are tied, opponent match win " +
            "percentage should be used as a tiebreaker " +
            "({} < {})".format(ranks[id4], ranks[id3]))
    print "11.  OMW percentage is being used as a tiebreaker"


# Support multiple tournaments
def testTournaments():
    wipeDatabase()
    t1 = createTournament()
    p1 = registerPlayer("Bilbo")
    p2 = registerPlayer("Gandalf")
    t2 = createTournament()
    p3 = registerPlayer("Frodo")
    p4 = registerPlayer("Sam")
    p5 = registerPlayer("Merry")
    p6 = registerPlayer("Pippin")
    attachPlayer(p2, t2)
    if countPlayers(t1) != 2:
        raise ValueError(
            "The first tournament should have two players")
    if countPlayers(t2) != 5:
        raise ValueError(
            "The second tournament should have five players")
    print "12. Multiple tournaments can be created"


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Starting extra credit tests..."
    testByes()
    testDraws()
    testTiebreaks()
    testTournaments()

    print "Success!  All tests pass!"
