#!/usr/bin/env bash

which node > /dev/null && which gcc > /dev/null || {
  echo "Installing node and gcc..."
  curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash - || { exit 1; }
  sudo apt-get install -y nodejs gcc || { exit 1; }
}
