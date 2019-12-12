cd ..
rmdir /s /q build
mkdir build
cd build

mkdir backend_tmp
mkdir backend_out
mkdir frontend_out 

cd backend_tmp

echo "Copying files"
call SET fromfolder=../../backend
FOR /F %%a IN (../../backend/included_files.txt) DO echo F|xcopy /h/y /z/i /k /f "%fromfolder%/%%a" "%%a"
call cp ../../backend/setup_compact.pyx .
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)

FOR /R %%x in (__init__.py) do ren "%%x" __init__.pyx
move mainServer.py mainServer.pyx
python setup_compact.pyx develop
IF %ERRORLEVEL% NEQ 0 (
  exit 1
)
del /S *.c
del /S *.py
del /S setup_compact.pyx
move mainServer.pyx mainServer.py
rmdir /S /Q build
FOR /R %%x in (__init__.pyx) do ren "%%x" __init__.py
dir
dir code_generator

copy ..\..\backend\windows.spec .
pyinstaller --clean -y windows.spec
IF %ERRORLEVEL% NEQ 0 (
  dir
  exit 1
)

call "dist/appServer/appServer.exe" -k=True
IF %ERRORLEVEL% NEQ 0 (
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


