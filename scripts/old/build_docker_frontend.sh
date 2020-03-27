
################### BUILD FRONTEND #######################
echo "----- Building frontend -----"
cd frontend/src
# npm run build
if [ $? -ne 0 ]; then exit 1; fi

echo "Copying file to frontend_out"

cd ../../

if [ ! -d frontend_out/ ]; then mkdir -p frontend_out/; fi
cp -R frontend/src/dist/* frontend_out/

################### MOVING EVERYTHING TO CORRECT PLACES #######################

ls -l
cp -R Docker/Frontend/ frontend_out

echo "Frontend folder"
ls -l frontend_out
