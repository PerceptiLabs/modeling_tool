CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
CONDA_ENV_FILE="../backend/environment.yml"

echo "Updating Homebrew..."
brew update --verbose

brew install rename

echo "Installing conda"
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O conda_installer.sh

mkdir ~/.conda 
echo "Running conda installer"
chmod +x conda_installer.sh
bash ./conda_installer.sh -b# -p $HOME/miniconda

echo "Adding conda to environment variables..."
export PATH="$HOME/miniconda/bin:$PATH"
eval "$(conda shell.bash hook)"

echo "Conda environment will be created from: $CONDA_ENV_FILE"
echo "Contents:"
cat "$CONDA_ENV_FILE"

echo "Creating environment"
conda env create --force --file $CONDA_ENV_FILE

echo "which python"
which python
