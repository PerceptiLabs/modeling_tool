FROM registry.access.redhat.com/ubi8/python-36

WORKDIR /app

# Copying directory inside docker
ADD fileserver /app/fileserver
COPY manage.py requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "django", "runserver", "0.0.0.0:8011", "--settings", "fileserver.settings", "--noreload"],
