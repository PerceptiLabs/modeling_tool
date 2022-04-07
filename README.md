# PerceptiLabs Modeling Tool

This is the main repo for the modeling tool, including the ML kernel,
frontend, and rygg

# Setting up your editor

Make sure that you set up your editor of choice with the following
instructions:
https://black.readthedocs.io/en/stable/integrations/editors.html:w


# How to build

## A Wheel

For when you want to replicate what the user sees:

```bash
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

```bash
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

# How to run a development environment as a docker-compose cluster
This will run all of the services in development mode with code reloading.

## Prerequisites
* docker from docker.com
* make (included with OSX & Linux, Windows get from chocolatey à la https://stackoverflow.com/a/57042516 )

## Quickstart
Just run it and watch the logs roll by
   ```bash
  cd docker/dev
  make dev_all
  docker-compose up
  # ... do stuff ...
  <ctrl-c> or close the terminal
  ```

## In the background

Use the `up` and `down` subcommands of `docker-compose`:
  ```bash
  docker-compose up -d
  # ... do stuff ...
  docker-compose down
  ```

To follow the logs of one service, e.g. the rendering kernel:
  ```bash
  docker-compose logs -f render
  ```

## Tests
To run integration tests against the docker-based services:
* rygg:
    ```bash
    python -m pytest -rfe --capture=tee-sys --host=localhost --port=80 --path="/rygg" --vol_map="${HOME}/Downloads/Perceptilabs_dev:/perceptilabs/Documents/Perceptilabs"
    ```
* kernel: TBD

## When to rebuild
* The docker files for development mode will mount your source directory into a volume so normal code changes will be picked up immediately.
* If you change your requirements.txt file or package.json in frontend, then you need to rebuild with `make`.

## Tear-down
* run `make clean` to tear everything down


# How to run a development environment as local scripts
0. To just run everything (with pyenv, venv, and pip on osx or linux):
    ```bash
    cd dev-env
    ./setup
    honcho start -f Procfile -e .env
    ```
   .... or run the following steps

1. Redis server
    ```bash
    docker run -it -p 6379:6379 redis
    ```
1. Rendering kernel
    ```bash
    cd backend
    PL_KERNEL_CELERY="1" PL_REDIS_URL="redis://localhost" AUTH_ENV=dev python main.py
    ```
1. Training worker
    ```bash
    cd backend
    PL_REDIS_URL="redis://localhost" AUTH_ENV=dev celery -A perceptilabs.tasks.celery_executor worker --loglevel=debug --queues=training --pool=threads
    ```
1. Flower (optional)
    ```bash
    cd backend
    PL_REDIS_URL="redis://localhost" celery -A perceptilabs.tasks.celery_executor flower --loglevel=debug
    ```
1. Rygg server
    ```bash
    cd rygg
    PL_FILE_SERVING_TOKEN=12312 PL_FILE_UPLOAD_DIR=$(pwd) PERCEPTILABS_DB=./db.sqlite3 container=xyz AUTH_ENV=dev python -m django migrate --settings rygg.settings
    PL_FILE_SERVING_TOKEN=12312 PL_FILE_UPLOAD_DIR=$(pwd) PERCEPTILABS_DB=./db.sqlite3 container=xyz AUTH_ENV=dev python -m django runserver 0.0.0.0:8000 --settings rygg.settings
    ```
1. Rygg worker
    ```bash
    cd rygg
    PL_FILE_SERVING_TOKEN=12312 PL_FILE_UPLOAD_DIR=$(pwd) PERCEPTILABS_DB=./db.sqlite3 container=a celery -A rygg worker -l INFO --queues=rygg
    ```
1. Frontend
    ```bash
    cd frontend
    npm install
    npm run-script start:web
    ```


## Local Build

You won't get auto-reload, but you'll get better handling of the fileserver token:

```bash
cd frontend

# Build the frontend static page
npm install
npm run build-render
rm -rf static_file_server/static_file_server/dist
mv src/dist static_file_server/static_file_server/
cd static_file_server

# create and activate a python virtual environment. For example:
python -m venv .venv
source .venv/bin/activate

# Set up and run the static_file_server
pip install --upgrade pip setuptools
pip install -r requirements.txt
python manage.py runserver
```

## Running dev env on Windows

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

# run the rendering kernel
cd "$PL_ROOT/backend"
AUTH_ENV=dev python main.py --mode=rendering --debug

# run rygg
cd $PL_ROOT/rygg
PL_FILE_SERVING_TOKEN=12312 PL_FILE_UPLOAD_DIR=$(pwd) AUTH_ENV=dev python manage.py runserver 0.0.0.0:8000

# Set up and run the static_file_server
cd $PL_ROOT/frontend
npm install
npm run build-render
rm -rf static_file_server/static_file_server/dist
mv src/dist static_file_server/static_file_server/
cd static_file_server
pip install --upgrade pip setuptools
pip install -r requirements.txt
PL_FILE_SERVING_TOKEN=12312 PL_KERNEL_URL=/kernel/ PL_RYGG_URL=/rygg/ PL_KEYCLOAK_URL=/auth/ python manage.py runserver 8080
```

In case of you are facing some issues with calling rygg, run `python manage.py migrate` inside `rygg` and run `python manage.py runserver`.

# How to release

1. Install and test pl-nightly to make sure it's shippable
1. Do the same tests against cd.perceptilabshosting.com
1. In the perceptilabs repo, update the VERSION file and tag the branch:
    ```bash
    # Stash your stuff
    CUR_BRANCH=$(git branch --show-current)
    export STASH=1; git stash | grep -i saved || { export STASH=0; }

    # switch to master
    git checkout master
    git pull -r
    git log
    # Review the log to pick the git commit to ship. Usually it'll be the one that was built for pl-nightly or for cd, which will be tagged as "docker_xxxx"
    export COMMIT_TO_SHIP=<the commit from the last step>
    git co $COMMIT_TO_SHIP

    # make the release tags
    git checkout -b tmp
    export PL_VERSION=<new version>
    scripts/make_release tmp $PL_VERSION origin

    # merge the tags into master
    git checkout master
    git merge tmp
    git push origin HEAD
    git branch -D tmp

    # switch back to your work
    git checkout $CUR_BRANCH
    [ $STASH -ne 1 ] || git stash pop
    ```
1. In pipelines
    1. Start "PerceptiLabs Docker" for $PL_VERSION tag. Note the build number from the URL of the build (a four-digit number currently starting with 7).
    1. Start "PerceptiLabs Pip" for $PL_VERSION tag
        1. Go to a previous release build
        1. Click "Run New"
        1. Select $PL_VERSION as the tag to build
1. When Perceptilabs Pip finishes, install the new perceptilabs from PyPI and do some sanity checks on it
1. When Perceptilabs Docker finishes, run the "Docker Release" pipeline
    - Use tag $PL_VERSION
    - Build ID to deploy: The build number from above
1. When Docker Release finishes, run "Release Airgapped"
    - Branch: master
    - Requested Version: <the release number>
1. When Docker Release finishes, run "Docker CD":
    - Branch: master
    - Release Channel: prod
    - Requested version: $PL_VERSION
    - GPUs: 1
    - CPUs: 4
    - Release environment: releasetest
    - DNS Subdomain: releasetest
    - Minutes to stay running: 120
    - SSH Key Name: <none>
1. When Docker Release finishes, go to releasetest.perceptilabshosting.com and do some sanity checks
