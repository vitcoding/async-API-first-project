#!/usr/bin/env bash

set -e

while ! nc -z api-service 8000; do 
    sleep 1; 
done 

pytest
