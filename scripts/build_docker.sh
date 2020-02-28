################### BUILD CORE BINARIES #######################
echo "Python location:"
which python

echo "Pip list:"
pip list

cd ..

# ---- Train models ----
echo "Training models"
cd backend/perceptilabs/insights/csv_ram_estimator/
python train_model.py data_1579288530.csv
cd ../../../../

# ----- Build backend ----
echo "----- Building backend -----"

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
cp ../../backend/setup.py .

echo "C compiling"
mv main.py main.pyx
find . -name "__init__.py" -exec rename -v 's/\.py$/\.pyx/i' {} \;
python setup.py build_ext --inplace --user
if [ $? -ne 0 ]; then exit 1; fi

echo "Cleaning up after the compilation"
find . -type f -name '*.c' -exec rm {} +
find . -type f -name '*.py' -exec rm {} +
rm -r build
mv main.pyx main.py
find . -name "__init__.pyx" -exec rename -v 's/\.pyx$/\.py/i' {} \;

echo "Adding app_variables"
cp ../../backend/perceptilabs/app_variables.json ./perceptilabs/

echo "Listing files to be included in build (contents of 'backend_out/')"
ls -l -R

################### BUILD FRONTEND #######################
echo "----- Building frontend -----"
cd ../../frontend/src
npm run build
if [ $? -ne 0 ]; then exit 1; fi

cp -r dist/* ../../build/frontend_out/

################### MOVING EVERYTHING TO CORRECT PLACES #######################
cd ../../

ls -l -a Docker/Frontend
cp -r Docker/Frontend/. build/frontend_out
cp -r Docker/Core/* build/backend_out
cp -r backend/code/templates/ build/backend_out/code/ #TODO: REMOVE

echo "Frontend folder"
ls -l -a -R build/frontend_out

echo "Core folder"
ls -R build/backend_out

#ls -l build/backend_out/code_generator
