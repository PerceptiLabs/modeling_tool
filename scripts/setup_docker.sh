echo "Installing gcc..."
sudo apt install gcc -y

echo "Installing requirements..."
python -m pip install --upgrade pip setuptools
pip install -r ../backend/requirements_linux.txt

echo "Installing npm..."
sudo apt install npm=6.13.2 -y

echo "npm version:"
npm -v

echo "node version:"
node -v

echo "Installing general npm packages"
cd ../frontend
npm install
echo "Installing browser packages"
cd src
npm install


