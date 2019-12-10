echo "Installing dependencies"
call python -m pip install --upgrade pip setuptools
call pip install -r requirements.txt
call pip install dask[array] --upgrade
call pip install pylint==2.4.3

cd ../backend
del *.c
echo "Running tests"
python python_error_checks.py
IF %ERRORLEVEL% EQU 2 (
  echo "Exiting from python error checks"
  exit 1
)
IF %ERRORLEVEL% EQU 1 (
  exit 0
)

REM FOR /F %%a IN (../scripts/included_files.txt) DO cython %%a 
REM echo %ERRORLEVEL%


