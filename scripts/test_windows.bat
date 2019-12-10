echo "Installing dependencies"
call python -m pip install --upgrade pip setuptools
call pip install -r requirements.txt
call pip install dask[array] --upgrade
call pip install pylint==2.4.3
call pip install pytest==5.3.1

cd ../backend
del *.c
echo "Running tests"
python python_error_checks.py
IF %ERRORLEVEL% EQU 2 (
  exit 1
)
IF %ERRORLEVEL% EQU 1 (
  exit 0
)

python -m pytest


REM FOR /F %%a IN (../backend/included_files.txt) DO (
REM   cython %%a
REM   IF %ERRORLEVEL% EQU 1 (
REM     exit 0
REM   )
REM ) 
REM echo %ERRORLEVEL%


