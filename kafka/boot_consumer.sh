#!/bin/bash

source venv/bin/activate
exec ./kafka/consumer.py -t google_scraper -f /home/portfolio/kafka/configs/consumer_google_chicago_1.config