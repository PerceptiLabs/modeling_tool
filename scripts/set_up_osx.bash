#!/usr/bin/env bash

which node || {
  echo "Updating Homebrew..."
  brew update --verbose
  brew install node

  echo "Fix  node links..."
  brew link --overwrite node # To replace old symbolic links
}
