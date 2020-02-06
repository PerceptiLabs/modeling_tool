cd ..

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

python setup.py build_ext sdist bdist_wheel

cd ..\backend_out
xcopy ..\backend_tmp\dist . /sy 