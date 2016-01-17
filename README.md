## Tournament-Organizer
A Python module with PostgreSQL database to keep track of players and matches in a Swiss-system Tournament

## Overview
The tournament defined here will use the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible. This setup provides
more playing experiences for participants as compared to elimination tournament - where players are eliminated in a single round. In a Swiss-system, the minimum number of rounds needed to determine a winner is same as elimination tournament:
`log (2, x)`, where 2 is base and x is the number of players. For a 16 players tournament, you will need 4 rounds to determine the winner. elimination tournament only needs `n-1` matches to find a winner (15 matches for 16 players), while a
Swiss-system needs `(n * log (2, x)) / 2` matches to find a winner (32 matches for 16 players).

## Included
- [tournament.py] (tournament.py) - All database schemas, connections, tournament operations are defined in this file. User has access to interactive mode and demo mode when executed this.
- [tournament_test.py] (tournament_test.py) - Unit tests provided by Udacity to debug and test the core functions provided by [tournament.py] (tournament.py). Extra functionalities such as odd number players, bye, omw are not tested.
- [tournament.sql] (tournament.sql) - Legacy file used to setup database schema before running tournament.py and tournament_test.py. [tournament.py] (tournament.py) currently has the same functionality by using `initConnect()` and `initTournament()`, where transactions are set to ISOLATION_LEVEL_AUTOCOMMIT in order run SQL commands within psycopg2 such as `CREATE DATABASE`. This file is provided to show my work history.

## Functions
The module provides the following functions:
- Passing all the unit tests provided in [tournament_test.py] (tournament_test.py)
- `registerPlayer(name)` - Adds a player to the tournament by putting an entry in the database. The database assigns an ID number to the player. Different players may have the same names but will receive different ID numbers.
- `countPlayers()` - Returns the number of currently registered players.
- `deletePlayers` - Clear out all the player records from the database.
- `reportMatch(winner, loser, random=False)` - Stores the outcome (wins and points) of a single match between two players in the database. If random is True, `coinToss` will be used to determine the winner/loser
- `coinToss()` - Returns a tuple of player 1 and player 2's points received and number of win received using Python's random module.
- `deleteMatches()` - Clear out all the match records from the database.
- `playerStandings(extended=False)` - Returns a list of (id, name, wins, matches) for each player, sorted by the number of wins each player has. If extended is True, returns a list of (id, name, matches, wins, OMW, points, bye) for each player, sorted by wins then OMW. OMW stands for Opponent Match Wins, the total number of wins by players they have played against. Players get 3 points for winning, 1 points for tie, and 0 point for losing. Bye (A free round where the player receives automatic win and 3 points. Used when there is odd number of players) is a Boolean value here to determine whether a player has received a bye yet. Each player can only receive one bye per tournament.
- `updateBye(bye)` - Update bye status of a selected player to True. Takes a player tuple from swissPairings() as argument.
- `deleteBye()` - Remove all the player Bye records from the database.
- `swissPairings(printing=False)` - Returns a list of pairs of players for the next round of a match according to Swiss-system. If printing is True, `printStandings` will be used to display the current standings in demo mode.
- `demoMode()` - Show case of how the module functions during a tournament. User can request up to 32 players in a tournament (with pre-defined names), and the function will match the players using `coinToss`, determine the current player standings, rinse, and repeat until set number of rounds (as determined by the equation above). Each standings will be displayed prior to the match.

## Work-in-Progress
- `rematchProof(standings)` - Update the order of current player standings to prevent players rematch. Currently not implemented.
- `interactiveMode()` - An interactive experience for user to access `demoMode()` and future functions. Currently implemented.

## Instructions
- Clone this repository
- Install [Vagrant][1] and [VirtualBox][2]
- Navigate to this directory in the terminal and enter `vagrant up` to initialize/power on the Vagrant virtual machine
- Enter `vagrant ssh` to log into the virtual machine
- Navigate to vagrant directory within the virtual machine by typing `cd /vagrant`
- Run [tournament_test.py] (vagrant/tournament/tournament_test.py) to perform unit tests
- Run [tournament.py] (vagrant/tournament/tournament.py) to engage in interactive mode, which provide extra functionalities such as:
  - Demo mode where the module shows a tournament test run with up to 32 players
  - Compatible with odd number of players by assigning one random player a "bye" for each round
  - Support games where draw is possible
  - When two players have the same number of wins, rank them according to OMW (Opponent Match Wins), the total number of wins by players they have played against

  [1]: https://www.vagrantup.com/downloads.html
  [2]: https://www.virtualbox.org/wiki/Downloads
