FROM continuumio/miniconda3
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY asdkljfhaskjdfhalksjdf234asdkljfhaskjdfhalksjdf234klj
RUN mkdir /news_mapper_django_docker
COPY requirements.txt /news_mapper_django_docker
COPY wheels/GDAL-2.2.4-cp37-cp37m-win32.whl /news_mapper_django_docker
COPY wheels/Fiona-1.7.13-cp37-cp37m-win32.whl /news_mapper_django_docker
COPY wheels/pyproj-1.9.5.1-cp37-cp37m-win32.whl /news_mapper_django_docker
COPY wheels/Rtree-0.8.3-cp37-cp37m-win32.whl /news_mapper_django_docker
COPY wheels/Shapely-1.6.4.post1-cp37-cp37m-win32.whl /news_mapper_django_docker
COPY wheels/numpy-1.15.2+mkl-cp37-cp37m-win32.whl /news_mapper_django_docker
WORKDIR /news_mapper_django_docker
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update && apt-get install -y && apt-get install build-essential libssl-dev -y && rm -rf /var/lib/apt/lists/*
RUN conda create --name news_mapper_django_docker python=3
RUN source activate news_mapper_django_docker
RUN pip install GDAL-2.2.4-cp37-cp37m-win32.whl
RUN pip install Fiona-1.7.13-cp37-cp37m-win32.whl
RUN pip install pyproj-1.9.5.1-cp37-cp37m-win32.whl
RUN pip install Rtree-0.8.3-cp37-cp37m-win32.whl
RUN pip install Shapely-1.6.4.post1-cp37-cp37m-win32.whl
RUN pip install numpy-1.15.2+mkl-cp37-cp37m-win32.whl
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 80
ENV NAME World
CMD ["python", "manage.py runserver"]
