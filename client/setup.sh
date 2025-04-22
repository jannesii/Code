sudo apt update -y
sudo apt install -y libcap-dev libatlas-base-dev ffmpeg libopenjp2-7
sudo apt install -y libcamera-dev
sudo apt install -y libkms++-dev libfmt-dev libdrm-dev
sudo apt install -y python3-pip python3-dev build-essential

python -m venv --system-site-packages .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install