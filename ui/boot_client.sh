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
exec gunicorn --config gunicorn_config.py next_word_engine:app

