#!/usr/bin/env bash

echo "Updating Homebrew..."
brew update --verbose
brew install node

echo "Fix  node links..."
brew link --overwrite node # To replace old symbolic links

echo "Installing pip requirements..."
python -m pip install --upgrade pip setuptools || { exit 1; }
pip install -r ../backend/requirements_posix_common.txt || { exit 1; }
