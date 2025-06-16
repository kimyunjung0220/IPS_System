import pyshark
from module import system_utils
import threading
import re
import json
import logging
import os
from datetime import datetime
from time import sleep
#<-----------------------------------------------------Packet Process------------------------------------------------------------>

logging.basicConfig(level=logging.CRITICAL)
system = system_utils

USER_PATH = os.popen('pwd').read().strip()

def trans_json(data : str) -> json:
    data_json = {}
    key = None
    object_key = None
    data = data.split("\n")
    for line in data:
        if line.startswith('Layer'):
            key = line
            data_json[key] = {}
            
        elif line.startswith('\t'):
            line = line.lstrip()
            if "=" in line:
                end = line.find("=")
            else:
                end = line.find(":")
                
            start = line.find("\t") + 1
            
            object_key = line[start:end]
            value = line[end+1:]
            data_json[key][object_key] = value
    system.wirte_packet(data_json)
    data = json.dumps(data_json, ensure_ascii=False)
    return data
    
        
def trans_data(data : str) -> dict:
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
    data = re.sub(ansi_escape, '', data)
    data = data.replace("\n:", "\n")
    return data

def get_packet(callback:None, func:None) -> json:
    get_sniff = pyshark.LiveCapture(interface=system.get_interface())
    for packet in get_sniff.sniff_continuously():
        packet = trans_data(str(packet))
        packet = trans_json(packet)
        detect = threading.Thread(target=detective_opensive, args=(packet,func), daemon=True)
        detect.start()
        callback('send_packet', {"data" : packet})
    
#<-----------------------------------------------------Detection Offensive------------------------------------------------------------>
class rule_memory():
    memory = []

def detective_opensive(data, func):
    packet = json.loads(data)
    layer_key = list(packet.keys())[1]

    #3계층 이상
    if layer_key == "Layer IP":
        sip = packet["Layer IP"]["Source Address"].strip()
        dip = packet["Layer IP"]["Destination Address"].strip()
        protocol = packet["Layer IP"]["Protocol"][1:4].strip()
        try:
            
            sport = int(packet[f"Layer {protocol}"]["Source Port"].strip())
        except:
            sport = None
            
        try:
            dport = int(packet[f"Layer {protocol}"][ "Destination Port"].strip())
        except:
            dport = None
    
    else: #2계층 이하
        for key, value in packet[layer_key].items():
            skey = key.lower()
            if ("sender ip" in skey) or ("source" in skey):
                sip = packet[layer_key][key]
            elif("taget" in skey) or ("destination" in skey):
                dip = packet[layer_key][key]
            sport = None
            dport = None

    #print(type(sip), dip, protocol,sport,dport)
    for rules in rule_memory.memory:
        detect = None
        flag, Dsip, Dsport, target, Ddip, Ddport, layer = rules[:7]
        msg, raw_input = rules[-2:]
        #check sip
        if not ((sip == Dsip) or (Dsip == "0.0.0.0")):
            continue
        
        #check dip
        if not ((dip == Ddip) or (Ddip == "0.0.0.0")):
            continue
        
        #check sport
        if not ((sport == Dsport) or (Dsport == None) or (sport == None)):
            continue
        
        #check dport
        if not ((dport == Ddport) or (Ddport == None) or (dport == None)):
            continue

        #프로토콜만 지정
        if(len(rules[6:len(rules)-2]) == 1):
            if "Layer" in layer:
                try:
                    packet[layer]
                    detect = True
                except KeyError:
                    detect = False

        #레이어에 옵션까지 있을 경우
        #content 부터 시작할 경우
        if "Content" in layer:
            for option in rules[6:len(rules)-2]:
                detect = False
                if not "Content" in option[0]:
                    print("너무 많은 인수 ")
                    break
                Mvalue = option[1]
                for key in packet.keys():
                    for obj, objvalue in packet[key].items():
                        if Mvalue.lower() in objvalue.lower():
                            detect = True

        #레이어를 지정했을 경우 시작할 경우
        else:
            try:
                for option in rules[7:len(rules)-2]:
                    detect = False
                    if "Layer" in option:
                        layer = option
                    else:
                        Mkey, Mvalue = option
                        Mkey = Mkey.strip().title()
                        Mvalue = Mvalue.strip()
                        if Mkey == "Flags":
                            flags = re.search(r'\((.*?)\)', packet[layer][Mkey]).group(1)
                            flags = flags.replace(" ", "").lower()
                            flags = flags.split(",")
                            flags = set(flags)
                            Mvalue = set(Mvalue.replace(" ", "").lower().split(","))
                            if flags == Mvalue:
                                detect = True
                        elif not Mkey == "Content":
                            val = packet[layer][Mkey]
                            if Mvalue in val:
                                detect = True
                        else:
                            for obj, obvalue in packet[layer].items():
                                if Mvalue in obvalue:
                                    detect = True
                    if not detect:
                        break
            except KeyError as e:
                continue
        #Detect, Drop, Detect-Drop
        if detect:
            time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            """data = {
                "time" : time,
                "Type" : Type,
                "msg" : msg,
                "user" : user,
                "value" : value
            }"""
            if flag == "Detect":
                send_msg = f"{time}\nDetect!\nrule: {raw_input}\nsrc_ip: {sip}\nsrc_port: {sport}\ndst_ip: {dip}\ndst_port: {dport}"
                func(time, flag, msg, "System", send_msg)

            elif flag == "Drop":
                send_msg = f"{time}\nBlock!\nrule: {raw_input}\nsrc_ip: {sip}\nsrc_port: {sport}\ndst_ip: {dip}\ndst_port: {dport}"
                func(time, flag, msg, "System", send_msg)
                
                #f"iptables -A INPUT -s {sip} -j DROP"
                
                iptables_cmd = ["iptables", "-A", "INPUT", "-s", sip, "-j", "DROP"]

                try:
                    subprocess.run(iptables_cmd, check=True)
                except:
                    msg = "Failed! Full resource!"

            elif flag == "Detect-Drop":
                send_msg = f"{time}\nDetect and Block!\nrule: {raw_input}\nsrc_ip: {sip}\nsrc_port: {sport}\ndst_ip: {dip}\ndst_port: {dport}"
                func(time, flag, msg, "System", send_msg)
                
                #f"iptables -A INPUT -s {sip} -j DROP"
                
                iptables_cmd = ["iptables", "-A", "INPUT", "-s", sip, "-j", "DROP"]
                
                try:
                    subprocess.run(iptables_cmd, check=True)
                except:
                    error = "Failed! Full resource!"
            else:
                msg = "error"

def init_memory():
    rule_memory.memory = []

    with open(f'{USER_PATH}/data/offensive/rule', 'r', encoding='utf-8') as f:
        rules = f.read().split("\n")
        if rules[0] == "":
            print("return")
            return
    ll = []
    try:
        for rule in rules:
            info = rule.split(" ")[:6]
            flag ,src_ip, src_port, target, des_ip, des_port = info
            src_ip = "0.0.0.0" if src_ip == "any" else src_ip
            des_ip = "0.0.0.0" if des_ip == "any" else des_ip
            src_port = None if src_port == "any" else int(src_port)
            des_port = None if des_port == "any" else int(des_port)
            ll = [flag ,src_ip, src_port, target, des_ip, des_port]
            matches = re.findall(r"\[[^\]]*\]", rule)

            for layer in matches:
                layer = layer.replace("[", "").replace("]", " ")
                if "msg" not in layer:
                    layer = layer.lower().split(":")
                else:
                    msg = layer.split(":")[1].rstrip()
                    continue
                if "layer" in layer[0]:
                    p = layer[1].replace(" ", "").upper()
                    ll.append(f"Layer {p}")

                elif "protocol" in layer[0]:
                    p = layer[1].upper().replace(" ", "")
                    ll.append(f"Layer {p}")

                elif "flag" in layer[0]:
                    ll.append(["Flags", layer[1].upper()])

                elif "conent" in layer[0]:
                    ll.append(["Content", layer[1].upper()])

                else:
                    ll.append([layer[0].strip().title(),layer[1].strip()])

            ll.append(msg)
            ll.append(rule)

            rule_memory.memory.append(ll)
    except ValueError as e:
        return
