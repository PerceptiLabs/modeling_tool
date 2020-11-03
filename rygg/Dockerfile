FROM registry.access.redhat.com/ubi8/python-36

# Define db ENV varibale to select database 
ENV DB_HOST="" \
    DB_PORT="5432" \
    DB_USER="" \
    DB_PASS="" \
    DB_NAME="" \
    DB="postgres"

LABEL name="PerceptiLabs-rygg-app" \
      maintainer="contact@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="1.0" \
      release="1"

WORKDIR /app

# Copying directory inside docker
ADD rygg /app/rygg
ADD licenses /licenses
COPY manage.py requirements.txt wait-for-db.py start.sh /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

CMD ["sh", "/app/start.sh"]

# Running following command after docker Run
# Docker build command -- docker build -t rygg .
# Docker run command -- docker run --rm --name=rygg -p 8000:8000 -v "$PWD":/app -e DB=postgres rygg:latest
