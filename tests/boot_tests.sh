#!/bin/bash

source venv/bin/activate
python tests/waitFor_testTopic_schemaRegistry.py 
exec tail -f /dev/null