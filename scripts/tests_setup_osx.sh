echo "Updating Homebrew..."
brew update --verbose

brew install rename

echo "Installing requirements..."
python -m pip install --upgrade pip setuptools
pip install -r ../backend/requirements_linux.txt

echo "which python"
which python
