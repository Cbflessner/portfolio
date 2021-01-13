#!/bin/bash

source venv/bin/activate
exec ./kafka/ngram_consumer_redis.py -t google_scraper -f consumer_google_chicago_1.config