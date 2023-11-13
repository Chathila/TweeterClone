drop table if exists includes;
drop table if exists lists;
drop table if exists retweets;
drop table if exists mentions;
drop table if exists hashtags;
drop table if exists tweets;
drop table if exists follows;
drop table if exists users;

create table users (
  usr         int,
  pwd	      text,
  name        text,
  email       text,
  city        text,
  timezone    float,
  primary key (usr)
);

INSERT INTO users VALUES
  (1, 'pass1', 'Nik', 'nik@email.com', 'Edmonton', 7),
  (2, 'pass2', 'Bob', 'bob@email.com', 'Calgary', 7),
  (3, 'pass3', 'Bill Longlastname', 'bill@email.com', 'Calgary', 7),
  (4, 'pass4', 'John', 'john@email.com', 'Red Deer', 7),
  (5, 'pass5', 'Matt', 'matt@email.com', 'Medicine Hat', 7),
  (6, 'pass6', 'Luke', 'luke@email.com', 'Edmonton', 7);

create table follows (
  flwer       int,
  flwee       int,
  start_date  date,
  primary key (flwer,flwee),
  foreign key (flwer) references users,
  foreign key (flwee) references users
);

INSERT INTO follows VALUES
  (1, 2, '2020-04-30'),
  (1, 3, '2023-05-09'),
  (2, 3, '2021-09-20'),
  (2, 4, '2019-04-30'),
  (3, 4, '2016-01-01'),
  (3, 5, '2022-12-04'),
  (4, 5, '2016-01-01'),
  (4, 6, '2022-12-04'),
  (5, 6, '2016-01-01'),
  (5, 1, '2022-12-04'),
  (6, 1, '2016-01-01'),
  (6, 2, '2022-12-04');

create table tweets (
  tid	      int,
  writer      int,
  tdate       date,
  text        text,
  replyto     int,
  primary key (tid),
  foreign key (writer) references users,
  foreign key (replyto) references tweets
);

INSERT INTO tweets VALUES
  (1, 1, '2020-04-30', 'Nik tweet 1', NULL),
  (2, 1, '2020-04-30', 'Nik tweet 2', NULL),
  (3, 2, '2020-05-30', 'Bob tweet 1', 1),
  (4, 2, '2020-04-30', 'Bob tweet 2', 2),
  (5, 3, '2019-04-30', 'Bill tweet 1', NULL),
  (6, 3, '2024-04-30', 'Bill tweet 2', NULL),
  (7, 4, '2020-04-30', 'John tweet 1', NULL),
  (8, 4, '2020-04-30', 'John tweet 2', NULL),
  (9, 5, '2020-04-30', 'Matt tweet 1', NULL),
  (10, 5, '2020-04-30', 'Matt tweet 2', NULL),
  (11, 6, '2020-04-30', 'Luke tweet 1', NULL),
  (12, 6, '2020-04-30', 'Luke tweet 2', NULL),
  (13, 2, '2021-04-30', 'Bob tweet 3', NULL),
  (14, 2, '2020-04-30', 'Bob tweet 4', NULL);

create table hashtags (
  term        text,
  primary key (term)
);
create table mentions (
  tid         int,
  term        text,
  primary key (tid,term),
  foreign key (tid) references tweets,
  foreign key (term) references hashtags
);
create table retweets (
  usr         int,
  tid         int,
  rdate       date,
  primary key (usr,tid),
  foreign key (usr) references users,
  foreign key (tid) references tweets
);

INSERT INTO retweets VALUES
  (1, 3, '2021-04-30'), -- Nik retweet Bob 1
  (1, 4, '2022-04-30'), -- Nik retweet Bob 2
  (3, 3, '2021-04-30'), -- Bill retweet Bob 1
  (3, 4, '2022-04-30'); -- Bill retweet Bob 2

create table lists (
  lname        text,
  owner        int,
  primary key (lname),
  foreign key (owner) references users
);
create table includes (
  lname       text,
  member      int,
  primary key (lname,member),
  foreign key (lname) references lists,
  foreign key (member) references users
);