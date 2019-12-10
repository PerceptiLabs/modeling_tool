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