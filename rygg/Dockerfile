FROM registry.access.redhat.com/ubi8/python-38

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
      release="1" \
      summary="A component of the PerceptiLabs modeling platform." \
      description="This image works in the background to support operations of the PerceptiLabs modeling platform."

USER 0
WORKDIR /app

# Copying directory inside docker
ADD licenses /licenses
COPY requirements.txt wait-for-db.py start.sh /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

ADD rygg /app/rygg
USER 1001

HEALTHCHECK \
  --interval=5s \
  --timeout=2s \
  CMD curl --fail localhost:8000/app/version/ || exit 1

CMD ["sh", "/app/start.sh"]
