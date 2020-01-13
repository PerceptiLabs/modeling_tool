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
mv mainServer.py mainServer.pyx
find . -name "__init__.py" -exec rename -v 's/\.py$/\.pyx/i' {} \;
python setup_compact.pyx develop --user
if [ $? -ne 0 ]; then exit 1; fi

echo "Cleaning up after the compilation"
find . -type f -name '*.c' -exec rm {} +
find . -type f -name '*.py' -exec rm {} +
rm setup_compact.pyx
rm -r build
mv mainServer.pyx mainServer.py
find . -name "__init__.pyx" -exec rename -v 's/\.pyx$/\.py/i' {} \;

echo "Listing files to be included in build (contents of 'backend_out/')"
ls -l

####################### Pyintaller -- REMOVE LATER ######################

echo "Running pyinstaller..."

cp ../../backend/linux.spec .
#cp ../../backend/common.spec common.py

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

################### BUILD FRONTEND #######################
echo "----- Building frontend -----"
cd ../../frontend/src
npm run build

cp dist/* ../build/frontend_out/

################### MOVING EVERYTHING TO CORRECT PLACES #######################
cd ../../
cp Docker/Fronend/* build/frontend_out
cp Docker/Core/* build/backend_out