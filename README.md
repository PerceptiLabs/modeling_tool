# Introduction 
This is the PerceptiLabs API server.

# Installation
1. Create a venv:
    ```
    python3 -m venv .venv
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
```
./manage.py runserver
```

# Run the server with env variable
```
DJANGO_DATABASE='postgres' ./manage.py runserver
```

# Play with the API
Go to http://localhost:8000

# Running Integration Tests
With a started server, run `python rygg/api/integration/run.py` and
wait for success
