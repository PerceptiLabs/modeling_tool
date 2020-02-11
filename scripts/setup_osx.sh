echo "Updating Homebrew..."
brew update --verbose

brew install rename

python -m pip install --upgrade pip setuptools
pip install -r ../backend/requirements_linux.txt

echo "Environment:"
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
