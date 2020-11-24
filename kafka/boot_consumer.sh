#!/bin/bash

source venv/bin/activate
exec ./kafka/consumer.py -t google_scraper -f /home/portfolio/kafka/kafka.config