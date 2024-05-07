#!/bin/sh

files=$(find data/*)

echo '================================================================================'
echo 'load tweets'
echo '================================================================================'
echo "$files" | time parallel python3 -u load_tweets.py --db=postgresql://hello_flask:hello_flask@localhost:13490/hello_flask_dev --inputs
