@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
IF EXIST c:\tools\miniconda3 (
  rmdir /s /q c:\tools\miniconda3
)

choco install nodejs --yes --version 12.10.0
choco install microsoft-visual-cpp-build-tools --version 14.0.25420.1 --yes
REM choco install windows-sdk-10.0 --yes

dir C:\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\SDK\ScopeCppSDK\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\SDK\ScopeCppSDK\SDK\


SET PATH=%PATH%;C:\hostedtoolcache\windows\Python\3.6.8\x64\Scripts

call python -m pip install --upgrade pip setuptools
call pip install -r requirements.txt
call pip install dask[array] --upgrade



call node --version
call npm --version

REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Microsoft SDKs\Windows\v10.0" /v ProductVersion

cd ..\frontend
call npm install
cd ..\scripts\ 