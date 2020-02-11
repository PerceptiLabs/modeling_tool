echo "Running build script."
echo "NOTE: Run this script in interactive mode: bash -i build.sh"

echo "Python location:"
which python

echo "Pip list:"
pip list

cd ..

# ---- Train models ----
echo "Training models"
cd backend/perceptilabs/insights/csv_ram_estimator/
python train_model.py data_1579288530.csv
if [ $? -ne 0 ]; then exit 1; fi
cd ../../../../

# ----- Build backend ----
echo "----- Building backend -----"
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
rsync -a ../../backend --files-from=../../backend/included_files.txt .
ls -l code_generator
cp ../../backend/setup.py .

echo "C compiling"
python setup.py build_ext --inplace
if [ $? -ne 0 ]; then exit 1; fi

echo "Cleaning up after the compilation"
find . -type f -name '*.c' -exec rm {} +
find . -type f -name '*.py' -exec rm {} +
rm setup.py
rm -r build

echo "Adding app_variables"
cp ../../backend/perceptilabs/app_variables.json ./perceptilabs/

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

echo "*************************************************************************************************"
echo "Testing to start the core"
./dist/appServer/appServer -k=True -l="INFO"
if [ $? -ne 0 ]; then exit 1; fi

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
cp build/*.zip ../build/frontend_out/
cp build/*.yml ../build/frontend_out/
   
    


