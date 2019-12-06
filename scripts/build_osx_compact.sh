echo "Running build script."
echo "NOTE: Run this script in interactive mode: bash -i build.sh"


echo "Adding conda to environment variables..."
export PATH="$HOME/miniconda/bin:$PATH"
eval "$(conda shell.bash hook)"

echo "Activating conda environment"
source ~/miniconda/etc/profile.d/conda.sh
conda activate py362_

echo "Python location:"
which python3

echo "Conda list:"
conda list

# ----- Build backend ----
echo "----- Building backend -----"
cd ..
rm -rf build
mkdir build
cd build/

echo "Cleaning up build directory"
rm -rf backend_tmp
rm -rf backend_out
rm -rf frontend_out

mkdir backend_tmp
mkdir backend_out
mkdir frontend_out

echo "Copying files files from ../../backend/"
cd backend_tmp/

rsync -a ../../backend --files-from=../../scripts/included_files.txt .

cp ../../backend/setup_compact.pyx .

mv mainServer.py mainServer.pyx

ls -l
ls -l analytics
exit 1
find . -name "__init__.py" -exec rename -v 's/\.py$/\.pyx/i' {} \;

ls -l

python setup_compact.pyx  build_ext --inplace
if [ $? -ne 0 ]; then exit 1; fi

find . -type f -name '*.c' -exec rm {} +
find . -type f -name '*.py' -exec rm {} +
rm setup_compact.pyx
rm -r build

mv mainServer.pyx mainServer.py
find . -name "__init__.pyx" -exec rename -v 's/\.py$/\.py/i' {} \;

echo "Listing files to be included in build (contents of 'backend_tmp/')"
ls -l

echo "Running pyinstaller..."
cp ../../backend/osx.spec .

pyinstaller --clean -y osx.spec
if [ $? -ne 0 ]; then exit 1; fi

if [ -e dist/appServer/libpython3.6m.so.1.0 ]
then
    # Randomly needed at Microsoft hosted agents.
    echo "libpython3.6m.so.1.0 exists, making defensive copy called libpython3.6m.so"
    cp dist/appServer/libpython3.6m.so.1.0 dist/appServer/libpython3.6m.so    
fi
# exit
chmod +x dist/appServer/appServer

# ./dist/appServer/appServer
# if [ $? -ne 0 ]; then exit 1; fi

echo "copying dist to 'backend_out/'"
cd ../backend_out/
cp -r ../backend_tmp/dist .

echo "listing backend_out/"
ls -l

echo "listing backend_out/dist/"
ls -l dist/




echo "Done building backend!"

# EXIT FOR NOW! TEMPORARY FIX!


# ----- Build frontend ----
echo "----- Building frontend -----"

cd ../../frontend/
rm -rf core
# rm -rf build

mkdir core
# mkdir build

echo "copying contents of '../build/backend_out/dist/appServer/' to 'core/'"
cp -r ../build/backend_out/dist/appServer/* core/ # DISABLE DURING QUICKER TESTING OF PIPELINE

echo "content of 'frontend'"
ls -l .

echo "Contents of 'core/'"
ls -l core/

echo "Pre building setup"
sudo chmod -R 777 core
xattr -cr .

echo "Building.."
npm run build

echo "Notarizing.."
sudo node notarize.js

echo "ls of 'frontend/build/'"
ls build/

echo "copying images to 'frontend_out/'"
cp build/*.dmg ../build/frontend_out/

   
    


