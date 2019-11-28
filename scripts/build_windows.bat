
call C:\tools\miniconda3\condabin\conda.bat init cmd.exe
call C:\tools\miniconda3\condabin\conda.bat activate py362_
call C:\tools\miniconda3\condabin\conda.bat env list
call C:\tools\miniconda3\condabin\conda.bat list

SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\include\10.0.18362.0\ucrt

cd ..
rmdir /s /q build
mkdir build
cd build

mkdir backend_tmp
mkdir backend_out
mkdir frontend_out 

cd backend_tmp
xcopy /s ..\..\backend . 

del minicodehq.py
del appOc.py
del a2cagent.py
del frontend_data_code.py
del core_test.py
del serverInterface.py

REM for /f %i in (..\..\..excluded_files.txt) do del %i

move setup.py setup.pyx
move mainServer.py mainServer.pyx

dir

python setup.pyx develop --user
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
del /S /Q *.py
move mainServer.pyx mainServer.py

dir

copy ..\..\backend\windows.spec .
pyinstaller --clean -y windows.spec
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)

exit /b

cd ..\backend_out
mkdir dist
xcopy ..\backend_tmp\dist dist\ /sy 

cd ..\..\frontend\

rmdir /s /q build
rmdir /s /q core
mkdir core
mkdir build

xcopy ..\build\backend_out\dist\appServer core\ /sy 
dir core

call npm run build
dir build

copy build\*.exe ..\build\frontend_out\ 

cd ..\scripts
