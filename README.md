# PerceptiLabs Modeling Tool

This is the main repo for the modeling tool, including the ML kernel,
frontend, and rygg

# How to build
## A Wheel

For when you want to replicate what the user sees:
```
cd scripts

# create and activate a python virtual environment. For example:
python -m venv .venv
. .venv/bin/activate

# build the wheel
python build.py wheel

# run it
perceptilabs
```

## The docker version

```
pushd scripts

# create and activate a python virtual environment. For example:
python -m venv .venv
. .venv/bin/activate

# build the images
python build.py docker all

popd

# run it
cd docker/compose
docker-compose up

# point your browser at http://localhost:8080
```


# How to run the frontend
## Dev Mode
For when you really need auto-reload capability.

```
cd frontend
npm install
npm run-script start:web
```

## Local Build

You won't get auto-reload, but you'll get better handling of the
fileserver token:

```
cd frontend

# Build the frontend static page
npm install
npm run build-render
rm -rf static_file_server/static_file_server/dist
mv src/dist static_file_server/static_file_server/
cd static_file_server

# create and activate a python virtual environment. For example:
python -m venv .venv
. .venv/bin/activate

# Set up and run the static_file_server
pip install --upgrade pip setuptools
pip install -r requirements.txt
python manage.py runserver
```

