#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    query = '''
    delete from matches;
    '''
    c.execute(query)
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    query = '''
    delete from players;
    '''
    c.execute(query)
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = psycopg2.connect("dbname=tournament")
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
    db = psycopg2.connect("dbname=tournament")
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
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    query = '''
    CREATE VIEW standing AS
        SELECT players.player_id,
               players.name,
               COALESCE(SUM(matches.win),0) as wins,
               COUNT(DISTINCT matches.match_num) as matches
        FROM players LEFT JOIN matches
        ON players.player_id = matches.player_id
        GROUP BY players.player_id
        ORDER BY wins DESC;

    SELECT * FROM standing;
    '''
    c.execute(query)
    standing = c.fetchall()
    db.close()
    return standing

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    query='''
    SELECT NEXTVAL('number');
    '''
    c.execute(query)
    n = c.fetchone()[0]
    query = '''
    insert into matches values (%s, %s, 1);
    '''
    c.execute(query, (n,winner))
    query='''
    insert into matches values (%s, %s, 0);
    '''
    c.execute(query, (n,loser))
    db.commit()
    db.close()


def swissPairings():
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
    ranking=0
    matches=[]
    for round in range(0,int(countPlayers()/2.)):

        matches.append((standings[ranking][0],
                        standings[ranking][1],
                        standings[ranking+1][0],
                        standings[ranking+1][1])
                      )
        ranking+=2
    return matches
