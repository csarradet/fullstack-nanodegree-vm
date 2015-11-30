
from the course's preconfigured Vagrant VM, do the needful to prepare the database for incoming connections:
    browse to the project directory
    > psql
    > \i tournament.sql

from the client:
    install psychopg2:
        > pip install psychopg2
    run tournament_test.py





The following assumptions are taken from the provided
WotC document describing the DCI's Swiss pairing system
(largely to save time--I actually play in M:TG tournaments
already, so I'm familiar with the rules system and many of
its quirks):
- A win counts as three points for matchmaking purposes
- A draw counts as one point
- A loss counts as zero points
- When appropriate, byes are awarded to the lowest-ranked
  player who has yet to receive a bye.

The following extra credit goals were attempted.  I left
the original tests in place, but added additional test cases
to tournament_test.py to demonstrate functionality:
 - Prevent rematches between players
 - If there is an odd number of players, award a bye
 - Support matches that result in a draw
 - Support tiebreaks via Opponent Match Win (OMW) percentage
 - Support multiple tournaments

 I changed how the deletePlayers() function works slightly.
 Multiple tourney support means that the player might still be
 enrolled somewhere else, so instead we just mark them as
 inactive within the given tourney and leave their record
 in the players table of the database.
