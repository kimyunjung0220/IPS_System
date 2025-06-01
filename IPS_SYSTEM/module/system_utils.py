
from datetime import datetime
import os
import time
import json
import psutil

USER_PATH = os.popen('pwd').read().strip() #/home/linux/Desktop/IPS_System-dev/IPS_SYSTEM

#<--------------------------------------------share memory------------------------------------------------>
class share_memory():
    hash_mem = {}

#<------------------------------------------OS info ---------------------------------------------------->
from scapy.all import get_if_list

NIC_LIST = ('eth', 'enp', 'ens', 'eno', 'enx', 'wlan', 'wlp', 'wlx')
def get_interface() -> str:
    interfaces = get_if_list()
    for interface in interfaces:
        if interface.startswith(NIC_LIST):
            return interface
        
#<----------------------------------------Log system decorator---------------------------------------------->
#system log decorator
from flask import request
from datetime import datetime
import time

#<--------------------------------------------------Web Event------------------------------------------------>


def logging_system(log_type=None, flag = None, msg = None, packet = None):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    date = datetime.now().strftime('%Y-%m-%d')
    
    log_msg = ""
    log_path = ""
    
    ip = request.remote_addr
    
    if "access" in log_type:
        if ip not in open("data/AccessList/Access_list.csv", 'r').read().split():
            log_msg = f"{now} : Access Denied from IP: {ip}\n"
            log_path = f'{USER_PATH}/log/Access_log/{date}_Access.log'
        else:
            log_msg = f"{now} : Access attempt from IP: {ip}\n"
            log_path = f'{USER_PATH}/log/Access_log/{date}_Access.log'
            
    if "auth" in log_type:
        log_msg = f"{now} - {msg} {ip}\n"
        log_path = f'{USER_PATH}/log/Auth_log/{date}_Auth.log'
        
    with open(log_path, 'a') as f:
        f.write(log_msg)

def wirte_packet(packet):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    date = datetime.now().strftime('%Y-%m-%d')
    packet = json.dumps(packet, indent=4)
    with open(f'{USER_PATH}/log/Packet_log/{date}_Packet_list.log', 'a') as f:
        f.write(f"{now} :\n{packet}\n")

#<--------------------------------------------------System Event------------------------------------------------>
def system_event(log_type = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            date = datetime.now().strftime('%Y-%m-%d')
            
            log_msg = ""
            log_path = ""
            
            if "system" in log_type:
                time.sleep(0.00001)
                Pname = 'IPS System' if func.__name__ == 'main' else func.__name__.replace('_', ' ')
                log_msg = f"{now} - Started {Pname}\n"
                log_path = f'{USER_PATH}/log/System_log/{date}_System.log'
            
            if log_type == "packet":
                packet = func(*args, **kwargs)
                with open(f'{USER_PATH}/log/Packet_log/{date}_Packet_list.log', 'a') as f:
                    f.write(f"{now} :\n{packet}\n")
                return packet
            
            if log_type != "packet":
                with open(log_path, 'a') as f:
                    f.write(log_msg)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

#<-------------------------------------------Crypto Utils-------------------------------------------------->
#AES 256
from Cryptodome.Cipher import AES 
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad

key = ""
iv = ""
#AES_Encrypt
def AES_Encrypt(plain_text : str) -> str:
    global key
    global iv
    return plain_text

def AES_Decrypt(chiper_text : str) -> str:
    global key
    global iv
    return chiper_text

#<-------------------------------------------------------------------------------------------------------------->
#Sha256
from hashlib import sha256

def SHA_Encrypt(plain_text : str) -> str:
    plain_text = plain_text.encode('utf-8')
    pepper = "IPS_SYSTEM".encode('utf-8')
    hash_text = sha256(plain_text + pepper).hexdigest()
    return hash_text
