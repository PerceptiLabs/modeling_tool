# FROM ubuntu:18.04
FROM registry.access.redhat.com/ubi8

# Define db ENV varibale to select database 
ENV DB_HOST=""
ENV DB_PORT="5432"
ENV DB_USER=""
ENV DB_PASS=""
ENV DB_NAME=""
ENV DB="postgres"

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

CMD python manage.py makemigrations
CMD python manage.py migrate --database=${DB}

CMD DJANGO_DATABASE=${DB} ./manage.py runserver 0.0.0.0:8000

# Docker build command -- docker build -t rygg:latest .
# Docker run command -- docker run --rm --name=rygg -p 8000:8000 -v "$PWD":/app -e DB=postgres rygg:latest