echo "Running build script."
echo "NOTE: Run this script in interactive mode: bash -i build.sh"

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

echo "Listing files to be included in build (contents of 'backend_tmp/')"
ls -l

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

chmod +x build/*.AppImage

echo "copying images to 'frontend_out/'"
echo "ls:"
ls build/*.AppImage
cp -r build/* ../build/frontend_out/

   
	    

