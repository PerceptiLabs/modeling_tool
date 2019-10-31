EXCLUDED_FILES=(
    'minicodehq.py'
    'appOc.py'
    'a2cagent.py'
    'frontend_data_code.py',
    'core_test.py',
    'serverInterface.py'
)

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
cp -r ../../backend/* .

for file in ${EXCLUDED_FILES[@]}
do
    echo "remove $file"
    rm $file
done


mv setup.py setup.pyx
mv mainServer.py mainServer.pyx

echo "Listing files to be included in build (contents of 'backend_tmp/')"
ls -l


echo "Compiling..."
python setup.pyx develop --user
rm *.py
mv mainServer.pyx mainServer.py

echo "Listing contents of 'backend_tmp/'"
ls -l



echo "Running pyinstaller..."

cp ../../backend/linux.spec .
#cp ../../backend/common.spec common.py

pyinstaller --clean -y linux.spec

#mv ../../backend/common.py ../../backend/common.spec

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

echo "Done building backend!"

 exit
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

   
	    

