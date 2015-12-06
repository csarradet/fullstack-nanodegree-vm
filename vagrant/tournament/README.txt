
from the course's preconfigured Vagrant VM, do the needful to prepare the database for incoming connections:
    browse to the project directory
    > psql
    > \i tournament.sql

from the client:
    install psychopg2:
        > pip install psychopg2
    run tournament_test.py




The following extra credit goals were attempted.  I left
the original tests in place, but added additional test cases
to tournament_test.py to demonstrate functionality:
 - Prevent rematches between players
 - If there is an odd number of players, award a bye
 - Support matches that result in a draw
 - Support tiebreaks via Opponent Match Win (OMW) percentage
 - Support multiple tournaments


The following assumptions are taken from the provided
WotC document describing the DCI's Swiss pairing system
and this doc on resolving tiebreakers:
https://www.wizards.com/dci/downloads/tiebreakers.pdf
(largely to save time--I actually play in M:TG tournaments
already, so I'm familiar with the rules system and many of
its quirks):
- A win counts as three points for matchmaking purposes.
- A draw counts as one point.
- A loss counts as zero points.
- When appropriate, byes are awarded to the lowest-ranked
  player who has yet to receive a bye.
- A bye has the same point value as a win, but doesn't contribute
  toward's a player's OMW percentage.
- To account for draws, a player's match win percentage
  is found by dividing their match points by three with a floor
  of 0.33 (to mitigate the impact of playing against extremely
  weak players).


 I changed how the deletePlayers() function works slightly.
 Multiple tourney support means that the player might still be
 enrolled somewhere else, so instead we have several ways of "removing" a player depending on the situation:
 - Delete their entire player record
 - Delete their enrollment record from a given tournament
 - Leave them attached to a tournament, but mark them as inactive for pairing purposes
