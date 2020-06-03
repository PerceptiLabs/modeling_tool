choco install nodejs --yes --version 12.10.0
choco install microsoft-visual-cpp-build-tools --version 14.0.25420.1 --yes
choco install git --yes
choco install --yes msys2

SET PATH=%PATH%;C:\hostedtoolcache\windows\Python\3.6.8\x64\Scripts
SET PATH=%PATH%;C:\msys64\mingw64\bin;C:\msys64\usr\bin
REM SET PATH=%PATH%;C:\tools\msys64\mingw64\bin;C:\tools\msys64\usr\bin

call python -m pip install --upgrade pip setuptools
call pip install "gym[atari]" 
call pip install -U git+https://github.com/Kojoley/atari-py.git
call pip install -r ../backend/requirements.txt
dir "c:\hostedtoolcache\windows\python\3.6.8\x64\Lib\site-packages\atari_py\"
dir "c:\hostedtoolcache\windows\python\3.6.8\x64\Lib\site-packages\"

call git config --global user.email "robert.l@perceptilabs.com"
git config --global user.name "Robert Lundberg"
call git clone https://github.com/Rolun/pyinstallerWindows.git
cd pyinstallerWindows
REM echo pulling correct pyinstaller
REM call git pull origin +refs/pull/3024/merge
call pip install .
IF %ERRORLEVEL% NEQ 0 ( exit 1 )
cd ..
echo Pyinstaller Version:
call pyinstaller --version

echo "Environemnt:"
call pip list

call node --version
call npm --version

REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Microsoft SDKs\Windows\v10.0" /v ProductVersion

cd ..\frontend
call npm install
cd ..\scripts\ 