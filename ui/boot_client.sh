#!/bin/bash

source venv/bin/activate
cd ui
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - --worker-tmp-dir /dev/shm next_word_engine:app

