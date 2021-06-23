FROM registry.access.redhat.com/ubi8/python-36

LABEL name="PerceptiLabs-fileserver-app" \
      maintainer="contact@perceptilabs.com" \
      vendor="PerceptiLabs" \
      version="1.0" \
      release="1" \
      summary="A component of the PerceptiLabs modeling platform." \
      description="This image works in the background to support operations of the PerceptiLabs modeling platform."

USER 0

WORKDIR /app

# Copying directory inside docker
ADD fileserver /app/fileserver
ADD licenses /licenses
ADD tutorial_data /tutorial_data
COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

USER 1001

HEALTHCHECK \
  --interval=1m \
  --timeout=2s \
  CMD curl --fail localhost:8011/version || exit 1

CMD python -m django runserver 0.0.0.0:8011 --settings fileserver.settings --noreload
