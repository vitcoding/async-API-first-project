#!/usr/bin/env bash

set -e

 while ! nc -z $SQL_HOST $SQL_PORT; do
     sleep 0.5
 done

 while ! nc -z $ELASTICSEARCH_HOST $ELASTICSEARCH_PORT; do
     sleep 0.5
 done

 while ! nc -z $REDIS_HOST $REDIS_PORT; do
     sleep 0.5
 done


gunicorn -c gunicorn.conf.py main:app
