# CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
# CONDA_ENV_FILE="../backend/environment_linux-py36.yml"

# # TODO: npm, gcc and conda versions should be explicitly declared to ensure reproducibility.

echo "Installing gcc..."
sudo apt install gcc -y

# echo "Downloading conda"
# wget $CONDA_URL -O conda_installer.sh

# echo "Running conda installer"
# chmod +x conda_installer.sh
# ./conda_installer.sh -b

# echo "Initializing conda"
# conda init

# echo "Conda environment will be created from: $CONDA_ENV_FILE"
# echo "Contents:"
# cat "$CONDA_ENV_FILE"

# echo "Creating environment"
# conda env create --force --file $CONDA_ENV_FILE

# echo "Environment:"
# conda list
conda remove --features mkl

python -m pip install --upgrade pip setuptools
pip install -r ../backend/requirements_linux.txt

echo "Installing npm..."
sudo apt install npm -y

echo "Installing npm packages"
cd ../frontend
npm install


