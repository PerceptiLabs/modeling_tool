EXCLUDED_FILES=(
    'minicodehq.py'
    'appOc.py'
    'a2cagent.py'
    'frontend_data_code.py'
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

echo "Copying Python files files from ../../backend/"
cd backend_tmp/
cp ../../backend/*.py .

for file in ${EXCLUDED_FILES[@]}
do
    rm $file
done

mv setup.py setup.pyx
mv mainServer.py mainServer.pyx

echo "Listing files to be included in build (contents of 'backend_tmp/')"
ls -l


echo "Compiling..."
python setup.pyx build_ext --inplace
mv mainServer.pyx mainServer.py

echo "Listing contents of 'backend_tmp/'"
ls -l


echo "Running pyinstaller..."
cp ../../backend/osx.spec .
pyinstaller --clean -y osx.spec

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

   
	    


