# FROM python:3
# ENV PYTHONUNBUFFERED 1
# RUN mkdir /code
# WORKDIR /code
# ADD requirements.txt /code/
# RUN conda install GDAL pyproj rtree fiona shapely && python -m pip install --user -r requirements.txt
# ADD . /code/
# CMD python3 manage.py runserver 0.0.0.0:$PORT

FROM continuumio/miniconda3

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV SECRET_KEY ${SECRET_KEY}
ENV NEWS_MAPPER_KEY ${NEWS_MAPPER_KEY}

ENTRYPOINT ["/bin/bash", "-c"]

COPY . /code
WORKDIR /code
ADD . /code

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update && apt-get install -y && apt-get install build-essential libssl-dev -y && rm -rf /var/lib/apt/lists/*

# ADD environment.yml /tmp/environment.yml
# WORKDIR /tmp

# RUN ["conda", "env", "create"]

RUN conda create --name news_mapper_conda_env python=3 && source activate news_mapper_conda_env && conda install GDAL Fiona pyproj rtree shapely && pip install --trusted-hose pypi.python.org -r requirements.txr



# EXPOSE 8000

# ENV NAME World

# CMD ["source activate news_mapper_conda_env && conda install GDAL Fiona pyproj rtree shapely && exec pip install --trusted-host pypi.python.org -r requirements.txt"]
# CMD ["python manage.py makemigrations && python manage.py migrate"]
# CMD ["python manage.py runserver 0.0.0.0:$PORT"]

CMD["exec python manage.py runserver 0.0.0.0:$PORT"]
