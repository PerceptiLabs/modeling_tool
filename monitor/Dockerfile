FROM python:3.10-alpine
ARG VERSION=dev

USER 0

WORKDIR /app
ADD requirements /app/requirements

RUN pip install --upgrade pip && \
    pip install -r requirements/prod.txt && \
    rm -rf requirements

ADD main.py .
WORKDIR /app/monitor
ADD monitor .
RUN echo "__version__ = '${VERSION}'" > __init__.py

WORKDIR /app
USER 1001
