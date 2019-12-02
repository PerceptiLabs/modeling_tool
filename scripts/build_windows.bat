
REM call C:\tools\miniconda3\condabin\conda.bat init cmd.exe
REM call C:\tools\miniconda3\condabin\conda.bat activate py362_
REM call C:\tools\miniconda3\condabin\conda.bat env list
REM call C:\tools\miniconda3\condabin\conda.bat list

REM echo "Setting Path:"
REM SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\include\10.0.10240.0\ucrt\io.h
REM SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\include\10.0.16299.0\ucrt\io.h
REM SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\include\10.0.17134.0\ucrt\io.h
REM SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\include\10.0.17763.0\ucrt\io.h
REM SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\include\10.0.18362.0\ucrt\io.h
REM path

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

REM move setup.py setup.pyx
REM move mainServer.py mainServer.pyx

REM cd code_generator
REM move __init__.py __init__.pyx

REM cd ../core_new/data
REM move __init__.py __init__.pyx

REM cd ../../

REM dir

REM python setup.pyx develop --user
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM del /S /Q *.py
REM del /S /Q *.c

move setup.py setup.pyx
copy /Y setup.pyx code_generator
copy /Y setup.pyx core_new
copy /Y setup.pyx core_new/data
copy /Y setup.pyx analytics

cd code_generator
mkdir code_generator
move __init__.py __init__.pyx
python setup.pyx develop
mv code_generator/* .
rm -rf code_generator
del *.c
del *.py
REM Xcopy /E /I /Y build/lib.win-amd64-3.6/code_generator .
REM rmdir /s /q build
ren __init__.pyx __init__.py
del setup.pyx
dir

cd ../core_new
python setup.pyx develop
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
mv data/* .
rm -rf data
del *.c
del *.py
REM Xcopy /E /I /Y build/lib.win-amd64-3.6/data .
REM rmdir /s /q build
ren __init__.pyx __init__.py
del setup.pyx
dir

cd ../../analytics
python setup.pyx develop
del *.c
del *.py
del setup.pyx
dir

cd ..
move mainServer.py mainServer.pyx
python setup.pyx develop
del *.c
del *.py
del setup.pyx
move mainServer.pyx mainServer.py

REM cd code_generator
REM move __init__.pyx __init__.py
REM Xcopy /E /I /Y build/lib.win-amd64-3.6/code_generator .

REM dir

REM cd ../core_new/data
REM move __init__.px __init__.py
REM Xcopy /E /I /Y build/lib.win-amd64-3.6/data .

REM dir

REM cd ../../

REM dir

copy ..\..\backend\windows.spec .
pyinstaller --clean -y windows.spec
IF %ERRORLEVEL% NEQ 0 (
  dir
  exit 1
)
echo Cert:
call c:\cert\signtool.exe
echo Windows kits
call "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe"
call "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist/appServer/*.exe"
IF %ERRORLEVEL% NEQ 0 (
  dir
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


