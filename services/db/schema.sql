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
create extension rum;

-- DISPLAY TWEETS indexes
CREATE INDEX idx_tweets_id_users ON tweets(id_users);
CREATE INDEX idx_users_id_users ON users(id_users);
CREATE INDEX idx_tweets_created_at ON tweets(created_at DESC);

-- USERNAME-PASSWORD MATCHING indexes
CREATE INDEX idx_users_username_password ON users(screen_name, passwrd);

-- LOOKUP USERNAME indexes
CREATE UNIQUE INDEX idx_users_username ON users(screen_name);

-- SEARCH indexes
create index idx_twt_text on tweets using rum(to_tsvector('simple', text)); --For FTS
create index idx_tweet_text_eng on tweets using rum(to_tsvector('english', text));


-- Unused for just here for tags
create index idx_tags_tag on tweet_tags using rum(to_tsvector('simple', tag));


