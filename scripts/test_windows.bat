echo "Installing dependencies"
call python -m pip install --upgrade pip setuptools
call pip install -r requirements.txt
call pip install dask[array] --upgrade
call pip install pylint

cd ../backend

echo "Running tests"
python python_error_checks.py develop