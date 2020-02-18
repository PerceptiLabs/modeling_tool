echo "Installing dependencies"
call python -m pip install --upgrade pip setuptools
call pip install "gym[atari]" 
call pip install -r ../backend/requirements.txt
call pip install dask[array] --upgrade
call pip install pylint==2.4.3
call pip install pytest==5.3.1