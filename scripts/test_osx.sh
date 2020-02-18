cd ../backend

echo "Running tests"
python python_error_checks.py
if [ $? -eq 2 ]; then exit 1; fi

python -m pytest
if [ $? -ne 0 ]; then exit 1; fi