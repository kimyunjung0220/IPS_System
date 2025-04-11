from scapy.all import get_if_list
from datetime import datetime
import time

NIC_LIST = ('eth', 'enp', 'ens', 'eno', 'enx', 'wlan', 'wlp', 'wlx')

#Get a NIC interface
def get_interface() -> str:
    interfaces = get_if_list()
    for interface in interfaces:
        if interface.startswith(NIC_LIST):
            return interface
        
#I have a fucking headache.
#Is this right??
#system log decorator
def log_event(log_type=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            date = datetime.now().strftime('%Y-%m-%d')
            
            log_msg = ""
            log_path = ""

            if log_type == "event":
                pass

            elif log_type == "system":
                time.sleep(0.00001)
                Pname = 'IPS System' if func.__name__ == 'main' else func.__name__.replace('_', ' ')
                log_msg = f"{now} - Started {Pname}\n"
                log_path = f'/home/linux/Desktop/IPS_System/log/System_log/{date}_System.log'

            elif log_type == "access":
                from flask import request
                ip = request.remote_addr
                log_msg = f"{now} : Access attempt from {ip}\n"
                log_path = f'/home/linux/Desktop/IPS_System/log/Access_log/{date}_Access.log'

            elif log_type == "packet":
                packet = func(*args, **kwargs)
                with open(f'/home/linux/Desktop/IPS_System/log/Packet_log/{date}_Packet_list.log', 'a') as f:
                    f.write(f"{now} :\n{packet}\n")
                return packet
            
            if log_type != "packet":
                with open(log_path, 'a') as f:
                    f.write(log_msg)

            return func(*args, **kwargs)
        return wrapper
    return decorator

    