Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

choco install nodejs --yes --version 12.10.0
#choco install mingw --yes
#choco install visualstudio2017buildtools --yes --version 15.8.2.0
choco install choco install microsoft-visual-cpp-build-tools --version 14.0.25420.1 --yes
choco install miniconda3 --yes --params"'/AddToPath /D:c:\tools'"

$env:Path = "C:\tools\miniconda3\Scripts;"+$env:Path
C:\tools\miniconda3\condabin\conda.bat init powershell
conda config --set ssl_verify no
conda env create --force --file "..\backend\environment.yml"
conda activate py362_

Write-Host "Listing conda env installations:"
conda list

Write-Host "Listing node and npm versions"
node --version
npm --version

Write-Host "Installing npm packages"
cd ../frontend
npm install

# Go back to scripts directory.
cd ..\scripts\ 

##### DEPRECATED STUFF BELOW #####
#Invoke-WebRequest -Uri "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" -OutFile "conda_installer.exe"
#$InstallDir="mycondadir"

##kolla detta: https://github.com/deto/Miniconda-Install/blob/master/Windows_Install.ps1
#Start-Process -FilePath "./conda_installer.exe" -ArgumentList "/S /v /D=$pwd\$InstallDir" -wait

#$env:Path = "$pwd\$InstallDir\Scripts;" + $env:Path
#$CONDA_ENV_FILE="..\backend\environment.yml"
