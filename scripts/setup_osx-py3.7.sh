CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
CONDA_ENV_FILE="../backend/environment_osx-py3.7.yml"

#echo "Installing Homebrew..."
#/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

echo "Updating Homebrew..."
brew update --verbose

brew install rename
#echo "Installing wget..."
#brew install wget

echo "Installing gcc..."
#brew install gcc

echo "Installing conda"
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O conda_installer.sh

mkdir ~/.conda 
echo "Running conda installer"
chmod +x conda_installer.sh
bash ./conda_installer.sh -b# -p $HOME/miniconda
#echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc


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

echo "Activating environment"
source ~/miniconda/etc/profile.d/conda.sh
conda activate py362_

echo "Environment:"
conda list
pip list

echo "which python"
which python

echo "Installing node..."
brew install node
brew link --overwrite node # To replace old symbolic links

echo "node.js version:"
node --version
echo "npm version:"
npm --version

echo "Installing npm packages"
cd ../frontend
npm install
