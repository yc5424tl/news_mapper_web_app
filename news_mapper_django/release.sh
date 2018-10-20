#!/usr/bin/env bash

add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
apt update
apt upgrade
apt install gdal-bin libgdal-dev

pip install conda
conda install gdal fiona rtree shapely pyproj
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
