echo "Adding conda to environment variables..."
export PATH="$HOME/miniconda/bin:$PATH"
eval "$(conda shell.bash hook)"

echo "Activating conda environment"
source ~/miniconda/etc/profile.d/conda.sh
conda activate py362_

cd ../backend

echo "Running tests"
python python_error_checks.py
if [ $? -eq 2 ]; then exit 1; fi

python -m pytest
if [ $? -ne 0 ]; then exit 1; fi