EXCLUDED_FILES=(
    'minicodehq.py'
    'appOc.py'
    'a2cagent.py'
    'frontend_data_code.py'
    'core_test.py'
    'serverInterface.py'
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

# for file in ${EXCLUDED_FILES[@]}
# do
#     rm $file
# done
rm minicodehq.py
rm appOc.py
rm a2cagent.py
rm frontend_data_code.py
rm core_test.py
rm serverInterface.py
rm lwInterface.py

mv setup.py setup.pyx

cp setup.pyx analytics/
cp setup.pyx code_generator/
cp setup.pyx core_new/
cp setup.pyx core_new/data/

ls -l

# analytics
cd analytics
python setup.pyx  build_ext --inplace
if [ $? -ne 0 ]; then exit 1; fi
rm *.py *.c *.pyx
ls -l

# code_generator
cd ../code_generator
mv __init__.py __init__.pyx
mkdir code_generator
python setup.pyx  build_ext --inplace
if [ $? -ne 0 ]; then exit 1; fi
mv code_generator/* .
rm -rf code_generator
rm *.py *.c
mv __init__.pyx __init__.py
rm *.pyx
ls -l

# core_new
cd ../core_new/
python setup.pyx  build_ext --inplace
if [ $? -ne 0 ]; then exit 1; fi
rm *.py *.c *.pyx
ls -l

# core_new.data
cd data/
mv __init__.py __init__.pyx
mkdir data/
python setup.pyx  build_ext --inplace
if [ $? -ne 0 ]; then exit 1; fi
mv data/* .
rm -rf data/
rm *.py *.c
mv __init__.pyx __init__.py
rm *.pyx
ls -l

# root
cd ../../
mv mainServer.py mainServer.pyx
python setup.pyx  build_ext --inplace
if [ $? -ne 0 ]; then exit 1; fi
rm *.py *.c
mv mainServer.pyx mainServer.py
rm *.pyx
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

echo "copying dist to 'backend_out/'"
cd ../backend_out/
cp -r ../backend_tmp/dist .

echo "listing backend_out/"
ls -l

echo "listing backend_out/dist/"
ls -l dist/


echo "Done building backend!"

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

   
    


