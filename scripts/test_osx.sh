cd ../backend

echo "Running tests"
python3 python_error_checks.py
if [ $? -eq 2 ]; then exit 1; fi

python3 -m pytest
if [ $? -ne 0 ]; then exit 1; fi