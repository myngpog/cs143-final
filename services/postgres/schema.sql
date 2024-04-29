CREATE EXTENSION postgis; --extension that helps with location-based data

\set ON_ERROR_STOP on --ensures no subsequent commands are run if an error occurs

BEGIN;

/*
 * Users may be partially hydrated with only a name/screen_name 
 * if they are first encountered during a quote/reply/mention 
 * inside of a tweet someone else's tweet.
 */
CREATE TABLE users (
    id_users BIGINT primary key,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    urls TEXT,
    friends_count INTEGER,
    listed_count INTEGER,
    favourites_count INTEGER,
    statuses_count INTEGER,
    protected BOOLEAN,
    verified BOOLEAN,
    screen_name TEXT,
    name TEXT,
    location TEXT,
    description TEXT,
    -- withheld_in_countries VARCHAR(2)[]
);

/*
 * Tweets may be entered in hydrated or unhydrated form.
 */
CREATE TABLE tweets (
    id_tweets BIGINT primary key,
    id_users BIGINT primary key,
    created_at TIMESTAMPTZ,
    -- in_reply_to_status_id BIGINT,
    -- in_reply_to_user_id BIGINT,
    -- quoted_status_id BIGINT,
    retweet_count SMALLINT,
    favorite_count SMALLINT,
    quote_count SMALLINT,
    -- withheld_copyright BOOLEAN,
    -- withheld_in_countries VARCHAR(2)[],
    source TEXT,
    text TEXT,
    country_code VARCHAR(2),
    state_code VARCHAR(2),
    lang TEXT,
    place_name TEXT,
    geo geometry
);

CREATE TABLE tweet_urls (
    id_tweets BIGINT primary key,
    urls TEXT
);

/*
 * =====INDEXES=====
 */
create index idx_users_sc on users(screen_name); --look for usernames
create index idx_created_at on users(created_at); --look for users based on acc creation
create index idx_location on users(location); --filter on location quickly



COMMIT;
