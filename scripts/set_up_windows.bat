choco install --yes nodejs --version 12.10.0
choco install --yes microsoft-visual-cpp-build-tools --version 14.0.25420.1
choco install --yes git
choco install --yes msys2

call python -m pip install --upgrade pip setuptools
call pip install "gym[atari]"
call pip install -U git+https://github.com/Kojoley/atari-py.git
call pip install -r ../backend/requirements_windows.txt
