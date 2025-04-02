USER_NAME=$(whoami)
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
