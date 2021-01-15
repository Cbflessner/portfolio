#!/bin/bash

source venv/bin/activate
cd ui
while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done
exec ./kafka/ngram_consumer_postgres.py -t google_scraper -f consumer_google_chicago_1.config