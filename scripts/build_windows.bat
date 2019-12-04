
REM call C:\tools\miniconda3\condabin\conda.bat init cmd.exe
REM call C:\tools\miniconda3\condabin\conda.bat activate py362_
REM call C:\tools\miniconda3\condabin\conda.bat env list
REM call C:\tools\miniconda3\condabin\conda.bat list

cd ..
rmdir /s /q build
mkdir build
cd build

mkdir backend_tmp
mkdir backend_out
mkdir frontend_out 

cd backend_tmp

call SET fromfolder=../../backend
echo "Scripts"
dir ../../scripts
echo %fromfolder%
dir %fromfolder%
call FOR /F %a IN (../../scripts/included_files.txt) DO echo F|xcopy /e/h/y /z/i /k /f "%fromfolder%/%a" "%a"
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
dir

exit

xcopy /s ..\..\backend . 
del minicodehq.py
del appOc.py
del a2cagent.py
del frontend_data_code.py
del core_test.py
del serverInterface.py
del lwInterface.py

move setup.py setup.pyx
copy /Y setup.pyx code_generator
copy /Y setup.pyx core_new
copy /Y setup.pyx core_new/data
copy /Y setup.pyx analytics

cd code_generator
mkdir code_generator
move __init__.py __init__.pyx
python setup.pyx develop
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
mv code_generator/* .
rm -rf code_generator
del *.c
del *.py
ren __init__.pyx __init__.py
del setup.pyx
dir

cd ../core_new
python setup.pyx develop
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
del *.c
del *.py
del setup.pyx
dir

cd data
cp ../../setup.pyx .
dir
mkdir data
move __init__.py __init__.pyx
python setup.pyx develop
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
mv data/* .
rm -rf data
del *.c
del *.py
ren __init__.pyx __init__.py
del setup.pyx
dir

cd ../../analytics
python setup.pyx develop
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
del *.c
del *.py
del setup.pyx
dir

cd ..
move mainServer.py mainServer.pyx
python setup.pyx develop
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
del *.c
del *.py
del setup.pyx
move mainServer.pyx mainServer.py



copy ..\..\backend\windows.spec .
pyinstaller --clean -y windows.spec
IF %ERRORLEVEL% NEQ 0 (
  dir
  exit 1
)
call "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist/appServer/*.exe"
IF %ERRORLEVEL% NEQ 0 (
  dir
  exit 1
)

cd ..\backend_out
mkdir dist
xcopy ..\backend_tmp\dist dist\ /sy 

cd ..\..\frontend\

rmdir /s /q core
mkdir core

xcopy ..\build\backend_out\dist\appServer core\ /sy 
dir core

call npm run build
IF %ERRORLEVEL% NEQ 0 (
  dir build
  exit 1
)
dir build

call "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 "build/*.exe"
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)

copy build\*.exe ..\build\frontend_out\ 

cd ..\scripts


