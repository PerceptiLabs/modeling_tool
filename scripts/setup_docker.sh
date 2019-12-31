CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
CONDA_ENV_FILE="../backend/environment.yml"

# TODO: npm, gcc and conda versions should be explicitly declared to ensure reproducibility.

echo "Installing gcc..."
sudo apt install gcc -y

echo "Downloading conda"
wget $CONDA_URL -O conda_installer.sh

echo "Running conda installer"
chmod +x conda_installer.sh
./conda_installer.sh -b

echo "Initializing conda"
conda init

echo "Conda environment will be created from: $CONDA_ENV_FILE"
echo "Contents:"
cat "$CONDA_ENV_FILE"

echo "Creating environment"
conda env create --force --file $CONDA_ENV_FILE

echo "Environment:"
conda list

echo "Installing npm..."
sudo apt install npm=6.4.1 -y

echo "node version:"
node -v

echo "Installing npm packages"
cd ../frontend/src
ls -l
npm install
echo "node version:"
node -v
ls -l


