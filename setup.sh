USER_NAME=$(whoami)
USER_PATH=$(pwd)

sudo cp -r "$USER_PATH"/IPS_SYSTEM /

sudo apt install python3 -y
sudo apt install python3-pip -y
sudo apt install wireshark -y
sudo apt install tshark -y
sudo usermod -aG wireshark "$USER_NAME"
sudo apt update
sudo pip3 install pyshark
sudo pip3 install flask
sudo pip3 install scapy
sudo pip3 install re
sudo pip3 install Pycryptodomex
sudo pip3 install flask-socketio
sudo pip3 install ipaddress
sudo pip3 install psutil

pip3 install pyshark
pip3 install flask
pip3 install scapy
pip3 install re
pip3 install Pycryptodomex
pip3 install flask-socketio
pip3 install ipaddress
pip3 install psutil

