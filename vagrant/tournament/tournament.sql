-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

drop database IF EXISTS tournament;
drop sequence IF EXISTS number;
create database tournament;
\c tournament;
create table players(player_id serial primary key, name text);
create table matches(match_num integer,
                     player_id integer references players,
                     win integer);
create sequence number;
--insert into players (name) values ('banana');
--insert into players (name) values ('cucumber');
--insert into players (name) values ('date');
--insert into matches values (1,1,1);
--insert into matches values (1,2,0);
--insert into matches values (2,3,1);
--insert into matches values (2,4,0);
--insert into matches values (3,1,1);
--insert into matches values (3,3,0);
--insert into matches values (4,2,1);
--insert into matches values (4,4,0);
