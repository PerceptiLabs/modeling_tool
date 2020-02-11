echo "Updating Homebrew..."
brew update --verbose

brew install rename

echo "Installing requirements..."
python3 -m pip install --upgrade pip setuptools
pip3 install -r ../backend/requirements_osx.txt

echo "which python"
which python3
