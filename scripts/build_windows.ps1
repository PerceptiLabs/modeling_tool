$EXCLUDED_FILES="minicodehq.py","appOc.py","a2cagent.py","frontend_data_code.py"

Write-Host "Running build script..."

$env:Path = "C:\tools\miniconda3\Scripts;"+$env:Path
C:\tools\miniconda3\condabin\conda.bat init powershell

conda activate py362_

Write-Host "Conda list:"
conda list

Write-Host "Listing gcc, node and npm versions"
#gcc --version
node --version
npm --version


Write-Host "----- Building backend -----"
cd ..
rm build -r -fo
mkdir build
cd build/

Write-Host "Cleaning up build directory"
if (Test-Path backend_tmp) {rm backend_tmp -r -fo}
if (Test-Path backend_out) {rm backend_out -r -fo}
if (Test-Path frontend_out) {rm frontend_out -r -fo}

mkdir backend_tmp
mkdir backend_out
mkdir frontend_out

echo "Copying Python files files from ../../backend/"
cd backend_tmp/
cp ../../backend/*.py .

Foreach ($file in $EXCLUDED_FILES)
{
  rm $file
}

mv setup.py setup.pyx
mv mainServer.py mainServer.pyx

Write-Host "Listing files to be included in build (contents of 'backend_tmp/')"
ls

Write-Host "Compiling..."
python setup.pyx develop --user
mv mainServer.pyx mainServer.py


echo "Listing contents of 'backend_tmp/'"
ls

Write-Host "Running pyinstaller..."
cp ../../backend/windows.spec .
pyinstaller --clean -y windows.spec


Write-Host "copying dist to 'backend_out/'"
cd ../backend_out/
cp ../backend_tmp/dist . -recurse

Write-Host "Done building backend!"


# ----- Build frontend ----
Write-Host "----- Building frontend -----"

cd ../../frontend/

if (Test-Path core) {rm core -r -fo}
if (Test-Path build) {rm build -r -fo}

mkdir core
mkdir build


Write-Host "copying contents of '../build/backend_out/dist/appServer/' to 'core/'"
cp ../build/backend_out/dist/appServer/* core/ -recurse

echo "Contents of 'core/'"
ls core/


echo "Building.."
npm run build

echo "copying images to 'frontend_out/'"
echo "ls:"
ls build/
cp build/*.exe ../build/frontend_out/