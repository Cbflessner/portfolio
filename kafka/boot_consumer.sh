#!/bin/bash

source venv/bin/activate
exec ./kafka/consumer.py -t google_scraper -f consumer_google_chicago_1.config