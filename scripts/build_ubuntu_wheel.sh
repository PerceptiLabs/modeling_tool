echo "Python location:"
which python3

echo "Conda list:"
conda list

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

mkdir backend_tmp
mkdir backend_out

echo "Copying files files from ../../backend/"
cd backend_tmp/
rsync -a ../../backend --files-from=../../backend/included_files.txt .
ls -l code_generator
cp ../../backend/setup.py .
cp ../../backend/setup.cfg .
cp "../../Docker/Core/licenses/PerceptiLabs EULA.txt" .
cp ../../backend/perceptilabs/app_variables.json ./perceptilabs/

echo "Listing files to be included in build (contents of 'backend_tmp/')"
ls -l -R

python setup.py build_ext bdist_wheel
if [ $? -ne 0 ]; then exit 1; fi

cd ../backend_out
cp ../backend_tmp/dist/* .