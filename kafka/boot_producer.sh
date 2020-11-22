#!/bin/bash

source venv/bin/activate
./producer.py -t google_scraper -f /home/portfolio/kafka/kafka.config
exec tail -f /dev/null