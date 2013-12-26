drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  image text,
  reference text
);

drop table if exists messages;
create table messages (
  id integer primary key autoincrement,
  name text not null,
  email text not null,
  message text not null,
  read integer not null default 0,
  location text not null
);

drop table if exists stats;
create table stats (
  id integer primary key autoincrement,
  name text not null,
  value integer not null
);

INSERT into stats (name, value) values ('visits', 264730)