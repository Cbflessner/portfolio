#!/bin/bash

source venv/bin/activate
./kafka/producer.py -t google_scraper -f /home/portfolio/kafka/configs/producer_google_chicago_1.config
exec tail -f /dev/null