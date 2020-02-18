cd ../backend

echo "Running critical error python tests"
python python_error_checks.py
if [ $? -eq 2 ]; then exit 1; fi

echo "Running python tests"
python -m pytest
if [ $? -ne 0 ]; then exit 1; fi