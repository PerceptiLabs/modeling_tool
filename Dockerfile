FROM ubuntu:18.04

# Define db ENV varibale to select database 
ENV DB_HOST="default"
ENV DB_PORT="default"
ENV DB_USER="default"
ENV DB_PASS="default"
ENV DB_NAME="default"
ENV DB="default"

LABEL name="PerceptiLabs-rygg-app" \
      maintainer="dev@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="1.0" \
      release="1"

# Install packages
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# Select the directory 
WORKDIR /app

# Copying directory inside docker
COPY . /app

# pip install
RUN pip install -r requirements.txt

# Running following command after docker Run

# CMD python manage.py makemigrations
# CMD python manage.py migrate --database                 //Commented it not sure we need to run migrate for external database

CMD DJANGO_DATABASE=${DB} ./manage.py runserver 0.0.0.0:8000

# Docker build command -- docker build -t rygg:latest .
# Docker run command -- docker run --rm --name=rygg -p 8000:8000 -v "$PWD":/app -e db=postgres rygg:latest