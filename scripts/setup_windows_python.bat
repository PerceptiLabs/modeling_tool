REM @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
REM IF EXIST c:\tools\miniconda3 (
REM   rmdir /s /q c:\tools\miniconda3
REM )

choco install nodejs --yes --version 12.10.0
choco install microsoft-visual-cpp-build-tools --version 14.0.25420.1 --yes
choco install git --yes
choco install msys2
REM choco install windows-sdk-10.0 --yes

REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\SDK\ScopeCppSDK\SDK\


REM set OLDPWD=%cd%
REM REM cd "C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build"
REM call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" x86_amd64
REM cd %VCINSTALLDIR%
REM call for /R %f in (*stdint.h) do set CL=-FI"%f"
REM call pip install pycrypto
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM cd %OLDPWD%

SET PATH=%PATH%;C:\hostedtoolcache\windows\Python\3.6.8\x64\Scripts
SET PATH=%PATH%;C:\msys64\mingw64\bin;C:\msys64\usr\bin
REM SET PATH=%PATH%;C:\tools\msys64\mingw64\bin;C:\tools\msys64\usr\bin

call python -m pip install --upgrade pip setuptools
call pip install "gym[atari]" 
call pip install --no-index -f https://github.com/Kojoley/atari-py/releases atari_py
call pip install -r requirements.txt
dir "c:\hostedtoolcache\windows\python\3.6.8\x64\Lib\site-packages\atari_py\"
dir "c:\hostedtoolcache\windows\python\3.6.8\x64\Lib\site-packages\"

call git config --global user.email "robert.l@perceptilabs.com"
git config --global user.name "Robert Lundberg"
call git clone https://github.com/Rolun/pyinstallerWindows.git
cd pyinstallerWindows
REM echo pulling correct pyinstaller
REM call git pull origin +refs/pull/3024/merge
call pip install .
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
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