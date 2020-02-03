echo "Running build script."
echo "NOTE: Run this script in interactive mode: bash -i build.sh"

echo "Activating conda environment"
conda activate py362_

echo "Python location:"
which python3


echo "Conda list:"
conda list

cd ..

# ---- Train models ----
echo "Training models"
cd backend/insights/csv_ram_estimator/
python train_model.py data_1579288530.csv
if [ $? -ne 0 ]; then exit 1; fi
cd ../../../

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
cp ../../backend/setup_compact.pyx .

echo "C compiling"
mv main.py main.pyx
find . -name "__init__.py" -exec rename -v 's/\.py$/\.pyx/i' {} \;
python setup_compact.pyx develop --user
if [ $? -ne 0 ]; then exit 1; fi

echo "Cleaning up after the compilation"
find . -type f -name '*.c' -exec rm {} +
find . -type f -name '*.py' -exec rm {} +
rm setup_compact.pyx
rm -r build
mv main.pyx main.py
find . -name "__init__.pyx" -exec rename -v 's/\.pyx$/\.py/i' {} \;

echo "Adding app_variables"
cp ../../backend/app_variables.json .

echo "Listing files to be included in build (contents of 'backend_tmp/')"
ls -l -R

echo "Running pyinstaller..."

cp ../../backend/linux.spec .

pyinstaller --clean -y linux.spec
if [ $? -ne 0 ]; then exit 1; fi

#mv ../../backend/common.py ../../backend/common.spec

if [ -e dist/appServer/libpython3.6m.so.1.0 ]
then
    # Randomly needed at Microsoft hosted agents.
    echo "libpython3.6m.so.1.0 exists, making defensive copy called libpython3.6m.so"
    cp dist/appServer/libpython3.6m.so.1.0 dist/appServer/libpython3.6m.so    
fi

chmod +x dist/appServer/appServer

echo "*************************************************************************************************"
echo "Testing to start the core"
./dist/appServer/appServer -k=True -l="INFO"
if [ $? -ne 0 ]; then exit 1; fi

echo "copying dist to 'backend_out/'"
cd ../backend_out/
cp -r ../backend_tmp/dist .

echo "Done building backend!"

# ----- Build frontend ----
echo "----- Building frontend -----"

cd ../../frontend/
rm -rf core
rm -rf build

mkdir core
mkdir build

echo "copying contents of '../build/backend_out/dist/appServer/' to 'core/'"
cp -r ../build/backend_out/dist/appServer/* core/

echo "Contents of 'core/'"
ls -l core/

echo "Building.."
npm run build

echo "copying images to 'frontend_out/'"
echo "ls:"
ls build/*.AppImage
cp build/*.AppImage ../build/frontend_out/
cp build/*.yml ../build/frontend_out/
cp build/*.deb ../build/frontend_out/

chmod +x ../build/frontend_out/*.AppImage

