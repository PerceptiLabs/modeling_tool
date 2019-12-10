cd ../backend

echo "Running tests"
python python_error_checks.py
if [ $? -eq 2 ]; then exit 1; fi
if [ $? -eq 1 ]; then exit 0; fi

python -m pytest