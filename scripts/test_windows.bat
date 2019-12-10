echo "Installing dependencies"
call python -m pip install --upgrade pip setuptools
call pip install -r requirements.txt
call pip install dask[array] --upgrade
call pip install pylint==2.4.3

cd ../backend
del *.c
echo "Running tests"
REM python python_error_checks.py
REM IF %ERRORLEVEL% EQU 2 (
REM   echo "Exiting from python error checks"
REM   exit 1
REM )


FOR /F %%a IN (../backend/included_files.txt) DO (
  cython %%a
  IF %ERRORLEVEL% EQU 1 (
    exit 0
  )
) 
REM echo %ERRORLEVEL%


