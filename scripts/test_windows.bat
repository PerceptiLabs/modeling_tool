cd ../backend

echo "Running critical error python tests"
python python_error_checks.py
IF %ERRORLEVEL% EQU 2 (
  exit 1
)
REM IF %ERRORLEVEL% EQU 1 (
REM   exit 0
REM )
echo "Running python tests"
python -m pytest
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)


REM FOR /F %%a IN (../backend/included_files.txt) DO (
REM   cython %%a
REM   IF %ERRORLEVEL% EQU 1 (
REM     exit 0
REM   )
REM ) 
REM echo %ERRORLEVEL%


