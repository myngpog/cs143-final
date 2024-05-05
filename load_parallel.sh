#!/bin/sh

# files=$(find data/*)

files='/data/tweets/geoTwitter21-01-01.zip
/data/tweets/geoTwitter21-01-02.zip
/data/tweets/geoTwitter21-01-03.zip
/data/tweets/geoTwitter21-01-04.zip
/data/tweets/geoTwitter21-01-05.zip
/data/tweets/geoTwitter21-01-06.zip
/data/tweets/geoTwitter21-01-07.zip
/data/tweets/geoTwitter21-01-08.zip
/data/tweets/geoTwitter21-01-09.zip
/data/tweets/geoTwitter21-01-10.zip'

echo '================================================================================'
echo 'load tweets'
echo '================================================================================'
echo "$files" | time parallel python3 -u load_tweets.py --db=postgresql://hello_flask:hello_flask@localhost:13490/hello_flask_dev --inputs
