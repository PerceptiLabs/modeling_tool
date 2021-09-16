# Introduction
This is the PerceptiLabs API server.

# Installation
1. Create a venv. Example with pyenv and pip:
    ```
    pyenv local 3.8.11
    pyenv exec python -m venv .venv
    source .venv/bin/activate
    ```

2. Install the dependencies:
    ```
    pip install --upgrade pip setuptools
    pip install -r requirements.txt
    ```

3. Create the database
    ```
    ./manage.py migrate
    ```

# Run the server
## For enterprise mode, trick it into thinking it's in a container:
```
PL_FILE_SERVING_TOKEN=12312 PL_TUTORIALS_DATA=$(git rev-parse --show-toplevel)/backend/perceptilabs/tutorial_data PL_FILE_UPLOAD_DIR=$(pwd) PERCEPTILABS_DB=./db.sqlite3 container=1 python manage.py runserver 0.0.0.0:8000
```
## For local mode:
```
PL_FILE_SERVING_TOKEN=12312 PL_TUTORIALS_DATA=$(git rev-parse --show-toplevel)/backend/perceptilabs/tutorial_data PL_FILE_UPLOAD_DIR=$(pwd) python manage.py runserver 0.0.0.0:8000
```


# Play with the API
```
export OAUTHLIB_INSECURE_TRANSPORT=1
```
To allow Oauth over insecure HTTP
Go to http://localhost:8000

# Running Integration Tests
1. From the rygg directory:
    1. migrate the db: `PERCEPTILABS_DB=$(pwd)/db.sqlite3 python manage.py migrate`
    1. start the server: `PL_FILE_SERVING_TOKEN=thetoken PL_TUTORIALS_DATA=$(git rev-parse --show-toplevel)/backend/perceptilabs/tutorial_data PL_FILE_UPLOAD_DIR=$(pwd) PERCEPTILABS_DB=$(pwd)/db.sqlite3 container=xyz python manage.py runserver 0.0.0.0:8000`
    1. start the worker: `PL_FILE_SERVING_TOKEN=thetoken PL_TUTORIALS_DATA=$(git rev-parse --show-toplevel)/backend/perceptilabs/tutorial_data PL_FILE_UPLOAD_DIR=$(pwd) PERCEPTILABS_DB=$(pwd)/db.sqlite3 container=a celery -A rygg worker -l INFO --queues=rygg`
1. In rygg/integration_tests, run: `python -m pytest`
1. wait for success
