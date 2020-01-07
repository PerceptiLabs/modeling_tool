################### BUILD CORE BINARIES #######################
echo "Activating conda environment"
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
rm -rf backend_out
rm -rf frontend_out

mkdir backend_out
mkdir frontend_out

echo "Copying files files from ../../backend/"
cd backend_out/
rsync -a ../../backend --files-from=../../backend/included_files.txt .
cp ../../backend/setup_compact.pyx .

echo "C compiling"
mv webServer.py webServer.pyx
find . -name "__init__.py" -exec rename -v 's/\.py$/\.pyx/i' {} \;
python setup_compact.pyx develop --user
if [ $? -ne 0 ]; then exit 1; fi

echo "Cleaning up after the compilation"
find . -type f -name '*.c' -exec rm {} +
find . -type f -name '*.py' -exec rm {} +
rm setup_compact.pyx
rm -r build
mv webServer.pyx webServer.py
find . -name "__init__.pyx" -exec rename -v 's/\.pyx$/\.py/i' {} \;

echo "Listing files to be included in build (contents of 'backend_out/')"
ls -l

################### BUILD FRONTEND #######################
echo "----- Building frontend -----"
cd ../../frontend/src
npm run build

cp -r dist/* ../../build/frontend_out/

################### MOVING EVERYTHING TO CORRECT PLACES #######################
cd ../../
ls -l
cp -r Docker/Frontend/* build/frontend_out
cp -r Docker/Core/* build/backend_out
cp backend/code_generator/train_normal_distr.py build/backend_out/code_generator   #TODO: REMOVE

echo "Frontend folder"
ls -l build/frontend_out

echo "Core folder"
ls -l build/backend_out

ls -l build/backend_out/code_generator