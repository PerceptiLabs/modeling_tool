EXCLUDED_FILES=(
    'minicodehq.py'
    'appOc.py'
    'a2cagent.py'
    'frontend_data_code.py'
    'core_test.py'
    'serverInterface.py'
    'lwInterface.py'
)


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

cp ../../backend/*.py .

mkdir analytics/
cp ../../backend/analytics/*.py analytics/

mkdir code_generator/
cp ../../backend/code_generator/*.py code_generator/

mkdir core_new/
cp ../../backend/core_new/*.py core_new/

mkdir core_new/data/
cp ../../backend/core_new/data/*.py core_new/data/


rm minicodehq.py
rm appOc.py
rm a2cagent.py
rm frontend_data_code.py
rm core_test.py
rm serverInterface.py
rm lwInterface.py

mv setup.py setup.pyx
mv mainServer.py mainServer.pyx

mv analytics/setup.py analytics/setup.pyx
mv code_generator/setup.py code_generator/setup.pyx
mv core_new/setup.py core_new/setup.pyx
mv core_new/data/setup.py core_new/data/setup.pyx

mv code_generator/__init__.py code_generator/__init__.pyx
mv core_new/data/__init__.py core_new/data/__init__.pyx

# analytics
cd analytics
python setup.pyx  build_ext --inplace
rm *.py *.c
mv __init__.pyx __init__.py
rm *.pyx

# code_generator
cd ../code_generator
mkdir code_generator
python setup.pyx  build_ext --inplace

mv code_generator/* .
rm -rf code_generator
rm *.py *.c
mv __init__.pyx __init__.py
rm *.pyx

# core_new
cd ../core_new/
python setup.pyx  build_ext --inplace
rm *.py *.c *.pyx

# core_new.data
cd data/
mkdir data/
python setup.pyx  build_ext --inplace
mv data/* .
rm -rf data/
rm *.py *.c
mv __init__.pyx __init__.py
rm *.pyx


# root
cd ../../
python setup.pyx  build_ext --inplace

rm *.py *.c
mv mainServer.pyx mainServer.py
rm *.pyx


echo "Listing files to be included in build (contents of 'backend_tmp/')"
ls -l

echo "Listing contents of 'backend_tmp/'"
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

chmod +x dist/appServer/appServer

echo "copying dist to 'backend_out/'"
cd ../backend_out/
cp -r ../backend_tmp/dist .

echo "listing backend_out/"
ls -l

echo "listing backend_out/dist/"
ls -l dist/




echo "Done building backend!"

# EXIT FOR NOW! TEMPORARY FIX!
exit


# ----- Build frontend ----
echo "----- Building frontend -----"

cd ../../frontend/
rm -rf core
rm -rf build

mkdir core
mkdir build

echo "copying contents of '../build/backend_out/dist/appServer/' to 'core/'"
cp -r ../build/backend_out/dist/appServer/* core/ # DISABLE DURING QUICKER TESTING OF PIPELINE

echo "Contents of 'core/'"
ls -l core/

echo "Building.."
npm run build

echo "ls of 'frontend/build/'"
ls build/

echo "copying images to 'frontend_out/'"
cp build/*.dmg ../build/frontend_out/

   
	    


