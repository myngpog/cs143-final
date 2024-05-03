#!/bin/sh

files=$(find data/*)

echo '================================================================================'
echo 'load tweets'
echo '================================================================================'
echo "$files" | time parallel python3 -u load_tweets.py --db=postgresql://postgres:pass@localhost:13490/ --inputs
