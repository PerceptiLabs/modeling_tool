
REM this depends on pwd being in the scripts directory
SET projectroot=%~dp0..
SET backend=%projectroot%\backend
SET wheelfiles=%projectroot%\wheelfiles
SET build=%projectroot%\build
SET tmp=%build%\tmp
set rygg=%projectroot%\rygg
ECHO Project root: %projectroot%

echo "Training models"
pushd %backend%\perceptilabs\insights\csv_ram_estimator
python train_model.py data_1579288530.csv || ( exit /b 1 )
popd

rmdir /s /q build
mkdir %tmp%

echo "Copying files"
FOR /F %%a IN (%projectroot%\scripts\included_files_common.txt) DO echo F&xcopy /h/y /z/i /k /f "%projectroot%/%%a" "%tmp%\%%a"
copy %backend%\perceptilabs\app_variables.json %tmp%\backend\perceptilabs\ || ( exit /b 1 )

copy %wheelfiles%\setup.py %tmp% || ( exit /b 1 )
copy %backend%\requirements_wheel_backend.txt %tmp% || ( exit /b 1 )
copy %wheelfiles%\setup.cfg %tmp% || ( exit /b 1 )
copy %wheelfiles%\setup.py %tmp% || ( exit /b 1 )
copy "%projectroot%\licenses\PerceptiLabs EULA.txt" %tmp% || ( exit /b 1 )
dir %tmp% || ( exit /b 1 )

copy %backend%\perceptilabs\tutorial_data %tmp%\backend\perceptilabs\ || ( exit /b 1 )

pushd %tmp%\backend
python setup.py build_ext bdist_wheel || ( exit /b 1 )
popd

mkdir %out%
xcopy %tmp%\dist %out% /sy  || ( exit /b 1 )
