echo "Installing gcc..."
sudo apt install gcc -y

echo "Installing requirements..."
python -m pip install --upgrade pip setuptools
pip install -r ../backend/requirements_linux.txt

echo "Installing npm..."
sudo apt install npm -y

echo "Installing npm packages"
cd ../frontend
npm install


