#!/usr/bin/env bash

set -e

python3 utils/wait_for_redis.py
python3 utils/wait_for_es.py

while ! nc -z api-service 8000; do 
    sleep 1; 
done 

pytest
