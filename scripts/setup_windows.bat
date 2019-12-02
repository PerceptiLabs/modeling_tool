@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
IF EXIST c:\tools\miniconda3 (
  rmdir /s /q c:\tools\miniconda3
)

dir 
exit 1
choco install nodejs --yes --version 12.10.0
choco install microsoft-visual-cpp-build-tools --version 14.0.25420.1 --yes
REM choco install windows-sdk-10.0 --yes
choco install miniconda3 --force --yes --params"'/AddToPath /D:c:\tools'"

REM dir C:\Program Files (x86)\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\SDK\ScopeCppSDK\
REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\SDK\ScopeCppSDK\SDK\


cd "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build"
call vcvarsall.bat x86_amd64
cd %VCINSTALLDIR%
for /R %f in (*stdint.h) do set CL=-FI"%f"
call pip install pycrypto


SET PATH=%PATH%;C:\tools\miniconda3\Scripts

call C:\tools\miniconda3\condabin\conda.bat init cmd.exe
call C:\tools\miniconda3\condabin\conda.bat config --set ssl_verify no
call C:\tools\miniconda3\condabin\conda.bat env create --force --file "..\backend\environment.yml"
call C:\tools\miniconda3\condabin\conda.bat activate py362_
call C:\tools\miniconda3\condabin\conda.bat env list

call C:\tools\miniconda3\condabin\conda.bat list

call node --version
call npm --version

REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Microsoft SDKs\Windows\v10.0" /v ProductVersion

cd ..\frontend
call npm install
cd ..\scripts\ 