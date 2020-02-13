cd ..

echo "Training models"
cd backend/perceptilabs/insights/csv_ram_estimator/
python train_model.py data_1579288530.csv

cd ../../../../

rmdir /s /q build
mkdir build
cd build

mkdir backend_tmp
mkdir backend_out

cd backend_tmp

echo "Copying files"
call SET fromfolder=../../backend
FOR /F %%a IN (../../backend/included_files.txt) DO echo F|xcopy /h/y /z/i /k /f "%fromfolder%/%%a" "%%a"
cp ..\..\backend\perceptilabs\app_variables.json ./perceptilabs/

call cp ../../backend/setup.py .
call cp ../../backend/setup.cfg .
call cp "../../Docker/Core/licenses/PerceptiLabs EULA.txt" .

python setup.py build_ext bdist_wheel

cd ..\backend_out
xcopy ..\backend_tmp\dist . /sy 

# Test installation
pip install --force --no-deps perceptilabs --find-links .
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
perceptilabs -k=True -l="INFO"
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)