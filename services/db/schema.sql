\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE urls (
    id_urls BIGSERIAL PRIMARY KEY,
    url TEXT UNIQUE
);

CREATE TABLE users (
    id_users BIGSERIAL primary key,
    created_at TIMESTAMPTZ,
    screen_name TEXT,
    password TEXT
);

CREATE TABLE tweets (
    id_tweets BIGSERIAL primary key,
    id_users BIGINT,
    created_at TIMESTAMPTZ,
    text TEXT
);

CREATE TABLE tweet_tags (
    id_tweets BIGINT,
    tag TEXT,
    PRIMARY KEY (id_tweets, tag),
    FOREIGN KEY (id_tweets) REFERENCES tweets(id_tweets)
);

/*
 * =====INDEXES=====
 */
create index idx_user_created_at on users(created_at); --look for users based on acc creation

create index idx_twt_created_at on tweets(created_at);
create index idx_twt_text on tweets using gin(to_tsvector('english', text));

create index idx_tags_tag on tweet_tags using gin(to_tsvector('english', tag));


COMMIT;
