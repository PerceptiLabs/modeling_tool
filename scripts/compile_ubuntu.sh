conda activate py362_

cd ..
rm -rf web_build
mkdir web_build

cd web_build

cp ../backend/*.py .

mkdir analytics/
cp ../backend/analytics/*.py analytics/

mkdir code_generator/
cp ../backend/code_generator/*.py code_generator/

mkdir core_new/
cp ../backend/core_new/*.py core_new/

mkdir core_new/data/
cp ../backend/core_new/data/*.py core_new/data/

rm minicodehq.py
rm appOc.py
rm a2cagent.py
rm frontend_data_code.py
rm core_test.py
rm serverInterface.py
rm lwInterface.py

mv setup.py setup.pyx
mv mainServer.py mainServer.pyx

mv analytics/setup.py analytics/setup.pyx
mv code_generator/setup.py code_generator/setup.pyx
mv core_new/setup.py core_new/setup.pyx
mv core_new/data/setup.py core_new/data/setup.pyx

mv code_generator/__init__.py code_generator/__init__.pyx
mv core_new/data/__init__.py core_new/data/__init__.pyx

# analytics
cd analytics
python setup.pyx develop --user
mv __init__.pyx __init__.py

# code_generator
cd ../code_generator
mkdir code_generator
python setup.pyx develop --user
mv code_generator/* .
rm -rf code_generator
mv __init__.pyx __init__.py

# core_new
cd ../core_new/
python setup.pyx develop --user

# core_new.data
cd data/
mkdir data/
python setup.pyx develop --user
mv data/* .
rm -rf data/
mv __init__.pyx __init__.py

# root
cd ../../
python setup.pyx develop --user
mv mainServer.pyx mv mainServer.py

# zip
cd ..
zip -r web_build.zip web_build/



