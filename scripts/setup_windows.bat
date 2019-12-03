@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
IF EXIST c:\tools\miniconda3 (
  rmdir /s /q c:\tools\miniconda3
)

dir 
call ls

REM choco install nodejs --yes --version 12.10.0
REM choco install microsoft-visual-cpp-build-tools --version 14.0.25420.1 --yes
REM REM choco install windows-sdk-10.0 --yes
REM choco install miniconda3 --force --yes --params"'/AddToPath /D:c:\tools'"

REM REM dir C:\Program Files (x86)\
REM REM dir C:\Program Files (x86)\Microsoft Visual Studio\
REM REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\
REM REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\
REM REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\SDK\ScopeCppSDK\
REM REM dir C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\SDK\ScopeCppSDK\SDK\


REM cd "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build"
REM call vcvarsall.bat x86_amd64
REM cd %VCINSTALLDIR%
REM for /R %f in (*stdint.h) do set CL=-FI"%f"
REM call pip install pycrypto


REM SET PATH=%PATH%;C:\tools\miniconda3\Scripts

REM call C:\tools\miniconda3\condabin\conda.bat init cmd.exe
REM call C:\tools\miniconda3\condabin\conda.bat config --set ssl_verify no
REM call C:\tools\miniconda3\condabin\conda.bat env create --force --file "..\backend\environment.yml"
REM call C:\tools\miniconda3\condabin\conda.bat activate py362_
REM call C:\tools\miniconda3\condabin\conda.bat env list

REM call C:\tools\miniconda3\condabin\conda.bat list

REM call node --version
REM call npm --version

REM REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Microsoft SDKs\Windows\v10.0" /v ProductVersion

REM cd ..\frontend
REM call npm install
REM cd ..\scripts\ 