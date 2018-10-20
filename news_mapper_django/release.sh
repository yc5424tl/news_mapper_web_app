#!/usr/bin/env bash

pip install conda
conda install gdal fiona rtree shapely pyproj
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
