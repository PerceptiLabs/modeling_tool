echo "Updating Homebrew..."
brew update --verbose

brew install rename

echo "Installing requirements..."
python3 -m pip3 install --upgrade pip3 setuptools
pip3 install -r ../backend/requirements_osx.txt

echo "Environment:"
pip3 list

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
