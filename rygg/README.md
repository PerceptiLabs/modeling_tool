# Introduction
This is the PerceptiLabs API server.

# Installation
Create a venv. Example with pyenv and pip:
```
# Set up a virtual environment (replace with conda, if desired)
pyenv local 3.8.11
pyenv exec python -m venv .venv
source .venv/bin/activate

# Install the dependencies:
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

# Run as local
```
export PL_FILE_SERVING_TOKEN=12312
export PL_FILE_UPLOAD_DIR=$(pwd)
export PERCEPTILABS_DB=./db.sqlite3
export AUTH_ENV=dev

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

# Run as enterprise
In three different terminals:
1. Start redis
    ```
    docker run -it -p 6379:6379 redis
    ```

1. Start the server
    ```
    export PL_FILE_SERVING_TOKEN=12312
    export PL_FILE_UPLOAD_DIR=$(pwd)
    export PERCEPTILABS_DB=./db.sqlite3
    export AUTH_ENV=dev
    export container=a

    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
    ```

1. Start the worker
    ```
    export PL_FILE_SERVING_TOKEN=12312
    export PL_FILE_UPLOAD_DIR=$(pwd)
    export PERCEPTILABS_DB=./db.sqlite3
    export AUTH_ENV=dev
    export container=a

    celery -A rygg worker -l INFO --queues=rygg
    ```

# Run integration tests
```
cd rygg/integration_tests
python -m pytest -rfe --capture=tee-sys
```

# Run unit tests
```
PL_FILE_SERVING_TOKEN=12312 PL_FILE_UPLOAD_DIR=~/Downloads/workingdir/data PERCEPTILABS_DB=./db.sqlite3 python manage.py
```