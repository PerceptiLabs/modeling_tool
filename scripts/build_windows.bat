
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
call SET destfolder="..\..\backend"

call FOR /F %a IN (../../scripts/included_files.txt) DO echo F|xcopy /e/h/y /z/i /k /f "%destfolder%/%a" "%a"

dir

exit
REM xcopy /s ..\..\backend . 
REM exit
REM REM del minicodehq.py
REM REM del appOc.py
REM REM del a2cagent.py
REM REM del frontend_data_code.py
REM REM del core_test.py
REM REM del serverInterface.py
REM REM del lwInterface.py

REM move setup.py setup.pyx
REM copy /Y setup.pyx code_generator
REM copy /Y setup.pyx core_new
REM copy /Y setup.pyx core_new/data
REM copy /Y setup.pyx analytics

REM cd code_generator
REM mkdir code_generator
REM move __init__.py __init__.pyx
REM python setup.pyx develop
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM mv code_generator/* .
REM rm -rf code_generator
REM del *.c
REM del *.py
REM ren __init__.pyx __init__.py
REM del setup.pyx
REM dir

REM cd ../core_new
REM python setup.pyx develop
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM del *.c
REM del *.py
REM del setup.pyx
REM dir

REM cd data
REM cp ../../setup.pyx .
REM dir
REM mkdir data
REM move __init__.py __init__.pyx
REM python setup.pyx develop
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM mv data/* .
REM rm -rf data
REM del *.c
REM del *.py
REM ren __init__.pyx __init__.py
REM del setup.pyx
REM dir

REM cd ../../analytics
REM python setup.pyx develop
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM del *.c
REM del *.py
REM del setup.pyx
REM dir

REM cd ..
REM move mainServer.py mainServer.pyx
REM python setup.pyx develop
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )
REM del *.c
REM del *.py
REM del setup.pyx
REM move mainServer.pyx mainServer.py



REM copy ..\..\backend\windows.spec .
REM pyinstaller --clean -y windows.spec
REM IF %ERRORLEVEL% NEQ 0 (
REM   dir
REM   exit 1
REM )
REM call "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist/appServer/*.exe"
REM IF %ERRORLEVEL% NEQ 0 (
REM   dir
REM   exit 1
REM )

REM cd ..\backend_out
REM mkdir dist
REM xcopy ..\backend_tmp\dist dist\ /sy 

REM cd ..\..\frontend\

REM rmdir /s /q core
REM mkdir core

REM xcopy ..\build\backend_out\dist\appServer core\ /sy 
REM dir core

REM call npm run build
REM IF %ERRORLEVEL% NEQ 0 (
REM   dir build
REM   exit 1
REM )
REM dir build

REM call "C:/Program Files (x86)/Windows Kits/10/bin/10.0.17763.0/x86/signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 "build/*.exe"
REM IF %ERRORLEVEL% NEQ 0 (
REM   exit 1
REM )

REM copy build\*.exe ..\build\frontend_out\ 

REM cd ..\scripts


