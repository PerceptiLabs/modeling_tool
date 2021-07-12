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
cd build/docker/compose
../../../scripts/dev_install

# point your browser at http://localhost
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
Do the following steps inside `backend` and `rygg` to set up environment for each services

1. Install Anaconda from here: https://docs.anaconda.com/anaconda/install/windows/
2. Open "Anaconda Prompt"
3. Create a new environment: `conda create -n pl_rygg python=3.7`
4. Create 2 more environments called `pl_backend`
5. cd to the rygg and backend folders and do the following:
6. Activate the proper environment: `conda activate pl_rygg` (`pl_rygg` for rygg, `pl_backend` for backend)
7. Update setuptools: `pip install --upgrade pip setuptools`
8. Install all dependencies: `pip install -r requirements.txt`

Now you have set up 3 environments, Now run the following to start services

```sh

PL_ROOT=$(git rev-parse--show-toplevel)

# run kernel
cd backend
python main.py

# run the rendering kernel
cd "$PL_ROOT/backend"
python main.py --mode=rendering --debug

# run rygg
cd $PL_ROOT/rygg
PL_FILE_SERVING_TOKEN=thetoken PL_TUTORIALS_DATA=$PL_ROOT/backend/perceptilabs/tutorial_data PL_FILE_UPLOAD_DIR=$(pwd) container=a python manage.py runserver 0.0.0.0:8000


# Set up and run the static_file_server
cd $PL_ROOT/frontend
npm install
npm run build-render
rm -rf static_file_server/static_file_server/dist
mv src/dist static_file_server/static_file_server/
cd static_file_server
pip install --upgrade pip setuptools
pip install -r requirements.txt
PL_FILE_SERVING_TOKEN=thetoken PL_KERNEL_URL=/kernel/ PL_RYGG_URL=/rygg/ PL_KEYCLOAK_URL=/auth/ python manage.py runserver 8080
```

In case of you are facing some issues with calling rygg, run `python manage.py migrate` inside `rygg` and run `python manage.py runserver`.

# How to release

## A Wheel

To release 0.12.34 from the master branch do this:
1. cd into scripts
2. Run ./release_pip master 0.12.34 origin
3. Follow the directions it prints about starting the pipeline
