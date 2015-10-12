#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from random import choice, shuffle
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def initConnect():
    """
    Connect to the default PostgreSQL database 'postgres' and create database
    'tournament'.
    """
    db=psycopg2.connect("dbname=postgres")
    db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    c = db.cursor()
    c.execute('drop database IF EXISTS tournament;')
    c.execute('create database tournament;')
    db.close()

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def initTournament():
    """Connect to the PostgreSQL database 'tournament' and initialize the
       database with necessary tables and sequence
       """
    db = connect()
    c = db.cursor()
    query = '''
    drop sequence IF EXISTS number;
    create table players(player_id serial primary key, name text);
    create table matches(match_num integer,
                         player_id integer references players,
                         play_against integer references players,
                         wins integer,
                         points integer);
    create sequence number;
    '''
    c.execute(query)
    db.commit()
    db.close()

def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    query = '''
    delete from matches;
    '''
    c.execute(query)
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    query = '''
    delete from players;
    '''
    c.execute(query)
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    query = '''
    select count(*) as total from players;
    '''
    c.execute(query)
    count = c.fetchone()
    db.close()
    return count[0]

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    query = '''
    insert into players (player_id, name) values (DEFAULT, %s);
    '''
    c.execute(query, (name,))
    db.commit()
    db.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    query = '''
    CREATE VIEW omw AS
      SELECT x.player_id,
             SUM(y.omw) as omw
      FROM
      (
        SELECT DISTINCT player_id, play_against
        FROM matches
      ) as x
      RIGHT JOIN
      (
        SELECT players.player_id,
               COALESCE(SUM(matches.wins),0) as omw
        FROM players LEFT JOIN matches
        ON players.player_id = matches.player_id
        GROUP BY players.player_id
      ) as y
      ON x.play_against = y.player_id
      GROUP BY 1
      ORDER BY 2 DESC;

    SELECT players.player_id,
           players.name,
           COUNT(DISTINCT matches.match_num) as matches,
           COALESCE(SUM(matches.wins),0) as wins,
           COALESCE(omw.omw,0),
           COALESCE(SUM(matches.points),0) as points
    FROM players LEFT JOIN matches ON players.player_id = matches.player_id
    LEFT JOIN omw ON players.player_id = omw.player_id
    GROUP BY players.player_id, omw.omw
    ORDER BY 4 DESC, 5 DESC;
    '''
    c.execute(query)
    standing = c.fetchall()
    db.close()
    return standing

def reportMatch(player1, player2):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    query='''
    SELECT NEXTVAL('number');
    '''
    c.execute(query)
    n = c.fetchone()[0]
    (player1_point, player1_win, player2_point, player2_win) = coinToss()
    query = '''
    insert into matches values (%s, %s, %s, %s, %s);
    insert into matches values (%s, %s, %s, %s, %s);
    '''
    c.execute(query, (n, player1, player2, player1_win, player1_point,
                      n, player2, player1, player2_win, player2_point))
    db.commit()
    db.close()


def swissPairings(printing=False):
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
    """
    standings=playerStandings()
    if printing==True:
        printStandings(standings)
    ranking=0
    matches=[]
    for round in range(0,int(countPlayers()/2.)):
        matches.append((standings[ranking][0],
                        standings[ranking][1],
                        standings[ranking+1][0],
                        standings[ranking+1][1]))
        ranking+=2
    return matches

def coinToss():
    """Returns a tuple of player 1 and player 2's points received and number of
       win received

    Used in demo mode to generate random events of player winning, losing, or
    drawing. For each call of coinToss(), players receive 3 points, 1 points,
    or 0 points for winning, drawing, or losing respectively. Players will also
    receive 1 or 0 win for each call of coinToss().

    Returns:
    A tuple contains (player1_point, player1_win, player2_point, player2_win)
    player1_point: point received by player 1 (either 0, 1, or 3)
    player1_win: number of win received by player 1 (either 1 or 0)
    player2_point: point received by player 2 (either 0, 1, or 3)
    player2_win: number of win received by player 2 (either 1 or 0)
    """
    player1_point=choice([0,1,3])
    if player1_point == 1:
        (player1_win, player2_point, player2_win) = (0, 1, 0)
    elif player1_point == 0:
        (player1_win, player2_point, player2_win) = (0, 3, 1)
    else:
        (player1_win, player2_point, player2_win) = (1, 0, 0)
    return (player1_point, player1_win, player2_point, player2_win)

def printStandings(standings):
    """
    Print the current Player Standings in a left-alinging format

    Args:
      standings: output from playerStandings()
    """

    column_width=20
    headers=('player_id', 'Name','match#', 'wins','omw','points')
    for header in headers:
        print header.ljust(column_width),
    print
    for x in standings:
        for data in x:
            print str(data).ljust(column_width),
        print
    print
#for n in range(10):
#    print coinToss()
