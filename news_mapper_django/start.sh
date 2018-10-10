#!/usr/bin/env bash

echo Starting Gunicorn.
exec gunicorn news_mapper.wsgi:application --bind 0.0.0.0:8000 --workers 3