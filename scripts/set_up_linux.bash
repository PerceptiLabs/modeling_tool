#!/usr/bin/env bash

echo "Installing node and gcc..."
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash - || { exit 1; }
sudo apt-get install -y nodejs gcc || { exit 1; }

echo "Installing pip requirements..."
python -m pip install --upgrade pip setuptools || { exit 1; }
pip install -r ../backend/requirements_posix_common.txt || { exit 1; }
