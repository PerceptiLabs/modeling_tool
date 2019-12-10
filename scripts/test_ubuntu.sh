CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
CONDA_ENV_FILE="../backend/environment.yml"

# TODO: npm, gcc and conda versions should be explicitly declared to ensure reproducibility.

echo "Installing gcc..."
sudo apt install gcc -y

conda activate py362_

cd ../backend

echo "Running critical error python tests"
python python_error_checks.py
if [ $? -eq 2 ]; then exit 1; fi
if [ $? -eq 1 ]; then exit 0; fi

echo "Running python tests"
python -m pytest