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
cd perceptilabs
mkdir tutorial_data
cd ..
call cp ../../backend/perceptilabs/tutorial_data/* ./perceptilabs/tutorial_data/

python setup.py build_ext bdist_wheel

cd ..\backend_out
xcopy ..\backend_tmp\dist . /sy 

REM pip install perceptilabs --find-links .
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM python -c "import perceptilabs"
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )