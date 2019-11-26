@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
IF EXIST c:\tools\miniconda3 (
  rmdir /s /q c:\tools\miniconda3
)

choco install nodejs --yes --version 12.10.0
choco install choco install microsoft-visual-cpp-build-tools --version 14.0.25420.1 --yes
choco install miniconda3 --force --yes --params"'/AddToPath /D:c:\tools'"


SET PATH=%PATH%;C:\tools\miniconda3\Scripts
call C:\tools\miniconda3\condabin\conda.bat init cmd.exe
call C:\tools\miniconda3\condabin\conda.bat config --set ssl_verify no
call C:\tools\miniconda3\condabin\conda.bat env create --force --file "..\backend\environment.yml"
call C:\tools\miniconda3\condabin\conda.bat env list
call C:\tools\miniconda3\condabin\conda.bat activate py362_


call C:\tools\miniconda3\condabin\conda.bat list

call pip list

call node --version
call npm --version

cd ..\frontend
call npm install
cd ..\scripts\ 