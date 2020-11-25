#!/bin/bash

source venv/bin/activate
cd ui
flask db upgrade
exec gunicorn --config gunicorn_config.py next_word_engine:app

