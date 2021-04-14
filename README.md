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

### Running dev env on Windows

Use Anaconda[https://www.anaconda.com/] to manage virtual environments.
Do the following steps inside `backend`, `rygg`, and `fileserver` to setup environment for each services

1. Install Anaconda from here: https://docs.anaconda.com/anaconda/install/windows/
2. Open "Anaconda Prompt"
3. Create a new environment: `conda create -n pl_rygg python=3.7`
4. Create 2 more environments called `pl_backend` and `pl_fileserver`
5. cd to the folder rygg, backend, fileserver and do the following
6. Activate the proper environment: `conda activate pl_rygg` (`pl_rygg` for rygg, `pl_backend` for backend, `pl_fileserver` for fileserver)
7. Update setuptools: `pip install --upgrade pip setuptools`
8. Install all dependencies: `pip install -r requirements.txt`
9. [Only for backend(kernel)] Install gym by following this: https://github.com/rybskej/atari-py up to and including the 3rd step and then `pip install "gym[atari]"` and `pip install -U git+https://github.com/Kojoley/atari-py.git`

Now you have setup 3 environments, Now run the following to start services

```sh

# run backend
cd ./backend
python main.py

# run rygg
cd ./rygg
python manage.py runserver

# run fileserver
cd ./fileserver
python manage.py runserver 8011

# Set up and run the static_file_server
pip install --upgrade pip setuptools
pip install -r requirements.txt
python manage.py runserver
```

In case of you are facing some issues with calling the rygg, run `python manage.py migrate` inside `rygg` and run `python manage.py runserver`.
