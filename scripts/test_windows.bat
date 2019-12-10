cd ../backend

echo "Running tests"
python python_error_checks.py
IF %ERRORLEVEL% EQU 2 (
  exit 1
)
REM IF %ERRORLEVEL% EQU 1 (
REM   exit 0
REM )

python -m pytest


REM FOR /F %%a IN (../backend/included_files.txt) DO (
REM   cython %%a
REM   IF %ERRORLEVEL% EQU 1 (
REM     exit 0
REM   )
REM ) 
REM echo %ERRORLEVEL%


