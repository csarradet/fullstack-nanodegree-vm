This project contains the files necessary to run a tournament bracketing system as described in FSND-Project 2.  From the course's preconfigured Vagrant VM, run the following commands to prepare the database for incoming connections:
    (browse to the project directory)
    > psql
    > \i tournament.sql

Once that is complete, run tournament_test.py to check our test cases.


---------------------


The following extra credit goals were attempted.  Test cases have been
added to the default suite to demonstrate functionality:
 - If there is an odd number of players, award a bye
 - Support matches that result in a draw
 - Support tiebreaks via Opponent Match Win (OMW) percentage
 - Support multiple tournaments


---------------------


The following assumptions are taken from the provided
WotC document describing the DCI's Swiss pairing system
and this doc on resolving tiebreakers:
https://www.wizards.com/dci/downloads/tiebreakers.pdf
(largely to save time--I actually play in M:TG tournaments
already, so I'm familiar with the pairing system):
 - A win counts as three points for matchmaking purposes.
   (This slightly changes what counts as a "win" according to the
   test cases.  Match Win Points are used for the actual matchmaking
   algorithm, so I did some handwaving to meet the spirit of the
   tests that expect, for example, one win after a match)
 - A draw counts as one point.
 - A loss counts as zero points.
 - When appropriate, byes are awarded to the lowest-ranked
  active player who has yet to receive a bye.
 - A bye has the same point value as a win, but doesn't contribute
  toward's a player's OMW percentage.


---------------------


 I slightly changed how the deletePlayers() function works,
 for two reasons:
 - Multiple tourney support means that the player might still be
   enrolled somewhere else, so it's possible we shouldn't delete
   them entirely.
 - Tiebreakers are decided by OMW percentage; even if a player
   drops from the tournament, their records are still relevant to
   other players.

 Instead of the stock behavior (option 1 below), we now have
 three ways of "removing" a player depending on the situation:
 - Delete their entire player record.
 - Delete their enrollment record for a given tournament.
 - Leave them attached to a tournament, but mark them as inactive for pairing
    purposes (preferred).
