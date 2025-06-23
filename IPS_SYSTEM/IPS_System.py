from flask import Flask, render_template, Response, request, url_for, redirect, make_response
from flask_socketio import SocketIO, emit
from collections import deque
from module import network_utils, system_utils
from datetime import datetime
import ipaddress
import threading
import os
import json
from time import sleep

#<-----------------------------------------------------init---------------------------------------------------------------------->

app = Flask(__name__)
app.secret_key = "IPS_SYSTEM"
system = system_utils
socketio = SocketIO(app=app, cors_allowed_origins="*")

session_storage= {}
"""
{
    "name" : name,
    "permit" : permit
}
    
"""
access_client = []

PERMIT = ["User", "Admin", "Super"]
USER_PATH = os.popen('pwd').read().strip() #/home/linux/Desktop/IPS_System-dev/IPS_SYSTEM

#<----------------------------------------------------memory queue -------------------------------------------------------------->

packet_queue = deque()
event_queue = deque()

#<--------------------------------------------------------Web Service------------------------------------------------------------>
######Access control 
@app.before_request
def accses_ctl():
    if request.remote_addr not in open('data/AccessList/Access_list.csv', 'r').read().split():
        system.logging_system(log_type="access", flag=True, msg=request.remote_addr)
        return render_template('block.html')
    system.logging_system(log_type="access",msg=request.remote_addr)

#####Rule
@app.route('/rule', methods=['GET', 'POST'])
def rule_page():
    Admin = None
    cookie = request.cookies.get('session_id')
    
    if not cookie:
        return redirect(url_for('login'))
    
    try:
        userinfo = session_storage[cookie]
        userpermit = userinfo["permit"]
        username = userinfo["name"]
        if userpermit in PERMIT[1:3]:
            Admin = True

        if request.method == 'GET':
            return render_template('rule.html', username=username, userpermit = userpermit, cip = request.remote_addr, Admin = Admin)
        
        if request.method =='POST':
            
            time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            date = datetime.now().strftime('%Y-%m-%d')
            
            flag = request.form.get("flag")
            
            if flag == "add_rule":
                rule = request.form.get("rule")
                input_rule = request.form.get("input_rule")
                res = check_rule(rule=rule, input_rule=input_rule)
                if not res:
                    value = f"{username} Added rule\nMaker: {username}\nMaker Permit: {userpermit}\n\nType: {rule}\nRule value: {input_rule}\n\nDate: {date} {time}"
                    event_io(time, "Event", "Add Rule", username, value)
                    data = f"{rule} {input_rule}"
                    socketio.emit('rule_list', {"data" : data}, namespace="/send_rule")
                else:
                    value = f"{username} Failed Add rule\nMaker: {username}\nMaker Permit: {userpermit}\n\nType: {rule}\nRule value: {input_rule}\nLog msg: {res}\n\nDate: {date} {time}"
                    event_io(time, "Event", "Failed Add Rule", username, value)
                    
                
            elif flag == "del_rule":
                rule = request.form.get("rule")
                del_info(username, userpermit, "rule", rule)
                network_utils.init_memory()
                res = None
                print(network_utils.rule_memory.memory)
        
        return render_template('rule.html', username=username, userpermit = userpermit, cip = request.remote_addr, Admin = Admin, msg = res)
    
    except:
        resp = make_response(redirect(url_for('login')))
        resp.delete_cookie('session_id')
        return resp

######admin page
#render page
@app.route('/admin_pages', methods=['GET', 'POST'])
def admin_page():
    cookie = request.cookies.get('session_id')
    if not cookie or cookie not in session_storage:
        resp = make_response(redirect(url_for('login')))
        resp.delete_cookie('session_id')
        return resp
    
    permit = session_storage[cookie]["permit"]
    name = session_storage[cookie]["name"]
    
    if permit not in PERMIT[1:]:
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        return render_template('admin.html', username=name, userpermit = permit)
    
    if request.method == 'POST':
        msg = None
        flag = request.form.get('flag')
        if flag == "add_member":
            Aname = request.form.get("add_name")
            Aid = request.form.get("add_id")
            Apw = request.form.get("add_passwd")
            Apermit = request.form.get('add_permit')
            
            msg = check_account(name, permit,Aname, Aid, Apw, Apermit)
            return render_template('admin.html', username=name, userpermit = permit, msg=msg)
        
        elif flag == "del_member":
            Daccount = request.form.get("account")
            Dpermit = request.form.get("permit")
            del_info(name, permit, "account", [Daccount, Dpermit])
        
        elif flag == "del_ip":
            ip = request.form.get("ip")
            
            if ip == "127.0.0.1":
                msg = "loopback 주소는 삭제할 수 없습니다."
                
            else:
                del_info(name, permit, "ip", ip)
                
            return render_template('admin.html', username=name, userpermit = permit, msg=msg)
        
        elif flag == "add_ip":
            ip = request.form.get('add_white') if request.form.get('add_white') != '0.0.0.0' else "Dont"
            
            try:
                ipaddress.ip_address(ip)
                check = True
            except ValueError:
                check = False
                msg = "올바르지 않은 IP주소"
                
            if check:
                with open('data/AccessList/Access_list.csv', 'r') as f:
                    ip_list = f.read().split("\n")
                if ip not in ip_list:
                    with open('data/AccessList/Access_list.csv', 'a') as f:
                        f.write(f"\n{ip}")
                        
                    time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    date = datetime.now().strftime('%Y-%m-%d')
                    
                    Msg = "Add White List"
                    Type = "Event"
                    value = f"{name} added {ip} to the White List\n\Maker: {name}\nMaker Permit : {permit}\n\nAdd IP : {request.remote_addr}\nDate : {date} {time}"
                    event_io(time=time,Type=Type,msg=Msg,user=name,value=value)
                else:
                    msg = "중복된 IP주소"  
            return render_template('admin.html', username=name, userpermit = permit, msg=msg)
            
      
###### index page
@app.route('/')
def index():
    Admin = None
    cookie = request.cookies.get('session_id')
    if not cookie:
        return redirect(url_for('login'))
    
    try:
        userinfo = session_storage[cookie]
        userpermit = userinfo["permit"]
        username = userinfo["name"]
        if userpermit in PERMIT[1:3]:
            Admin = True
        return render_template('index.html', username=username, userpermit = userpermit, cip = request.remote_addr, Admin = Admin)
    
    except:
        resp = make_response(redirect(url_for('login')))
        resp.delete_cookie('session_id')
        return resp

######logout
@app.route('/logout')
def logout():
    cookie = request.cookies.get('session_id')
    if cookie in session_storage:
        session_storage.pop(cookie)
        
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('session_id')
    try:
        msg = f"{system.share_memory.hash_mem[request.remote_addr]} has logged out from"
    except:
        msg = f"Suspicious access attempt was blocked from"
    system.logging_system(log_type="auth", msg=msg)
    return resp

######login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        uid = request.form.get('username')
        upw = system.SHA_Encrypt(request.form.get('password'))
        
        with open('data/UserData/UserTable', 'r') as file:
            f = file.read().split('\n')

        for data in f:
            if data.strip():
                info = data.split(":")
                name, permit  = info[0][1:], info[3]
                id, pw = info[1:3]
                if id == uid and pw == upw:
                    msg = f"{name} has logged in from"
                    resp = make_response(redirect(url_for('index')))
                    cookie = os.urandom(32).hex()
                    system_utils.share_memory.hash_mem[request.remote_addr] = name
                    session_storage[cookie] = {
                        "name" : name,
                        "permit" : permit
                    }
                    resp.set_cookie("session_id", cookie)
                    system.logging_system(log_type="auth", msg=msg)
                    return resp
                
        msg = "Login failed from"
        error = "아이디 또는 비밀번호가 일치하지 않습니다."
        system.logging_system(log_type="auth", msg=msg)
        return render_template('login.html', error=error)
    
######register
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    msg = None
    users = []
    
    with open(f'{USER_PATH}/data/UserData/UserTable') as f:
        for line in f:
            user_data = line.strip().split(':')
            users.append(user_data[1])
        f.close()
        
    if request.method == 'GET':
        return render_template('register.html', error=error, msg=msg)
    
    if request.method == 'POST':
        
        time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        date = datetime.now().strftime('%Y-%m-%d')
        
        error = None
        msg = None
        
        name = request.form.get('name')
        id = request.form.get('username')
        pw = request.form.get('password')
        cpw = request.form.get('confirm_password')
        permit = request.form.get('permit')
        
        if (permit == "Super") or (permit not in PERMIT[:3]):
            msg = "비정상 트래픽. Don't hacking!"
    
        if id in users:
            error = "이미 존재하는 아이디입니다."
        
        elif len(pw) < 12:
            error = "비밀번호는 12자 이상으로 설정해야 합니다."
        
        elif pw != cpw:
            error = "비밀번호가 일치하지 않습니다."
        
        elif id == pw:
            error = "아이디와 비밀번호는 동일할 수 없습니다."
        
        if not error:
            msg = "회원가입 성공"      
            pw = system.SHA_Encrypt(pw)

            
            with open('data/UserData/UserTable', 'a') as f:
                f.write(f"\n#{name}:{id}:{pw}:{permit}")
                f.close()
            value = f"{name} Register\n\nName: {name}\nPermit : {permit}\n\nIP : {request.remote_addr}\nDate : {date} {time}"
            event_io(time, "Register", "Register", name, value)
            
        else:
            value = f"Register Failed\n\nLog msg : {error}\nIP : {request.remote_addr}\nDate : {date} {time}"
            event_io(time, "Register", "Failed Register", name, value)
        return render_template('register.html', error=error, msg=msg)
    
    
#<----------------------------------------------------------Socket io------------------------------------------------------------>
#send rule
@socketio.on('request_data', namespace="/send_rule")
def send_rule():
    data= None
    with open(f"{USER_PATH}/data/offensive/rule", 'r') as f:
        rules = f.read().split("\n")
    for data in rules:
        socketio.emit('rule_list', {"data" : data}, namespace="/send_rule",  to=request.sid)


#send account
@socketio.on('request_data', namespace="/send_account")
def send_account():
    user_tables = list_account()
    for name, user_id, user_passwd, permit in user_tables:
        user_dic = {}
        user_dic['name'] = name
        user_dic['userid'] = user_id
        user_dic['permit'] = permit
        socketio.emit('user_account', {'data' : user_dic}, namespace="/send_account", to=request.sid)

        
#send white list
@socketio.on('request_data', namespace="/send_whitelist")
def send_account():
    with open('data/AccessList/Access_list.csv', 'r') as f:
        white_list = f.read().split('\n')
        
    for ip in white_list:
        socketio.emit('white_list', {'data' : ip}, namespace="/send_whitelist", to=request.sid)
        
#send event list
@socketio.on('request_data', namespace="/send_event")
def event_list():
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H')
    try:
        with open(f'{USER_PATH}/log/Event_log/{date}-{time}_Event.log', "r") as f:
            res = f.read().split("\n")
        for event in res:
            if not event.strip():
                continue
            event = json.loads(event)
            data = {
            "time" : event['time'],
            "Type" : event['Type'],
            "msg" : event['msg'],
            "user" : event['user'],
            "value" : event['value']
            }
            socketio.emit('event_list', {'data' : data}, namespace="/send_event", to=request.sid)
    except:
        return

#send event
def event_io(time, Type, msg, user, value):
    date = datetime.now().strftime('%Y-%m-%d')
    hour = datetime.now().strftime('%H')
    data = {
        "time" : time,
        "Type" : Type,
        "msg" : msg,
        "user" : user,
        "value" : value
    }
    with open(f'{USER_PATH}/log/Event_log/{date}-{hour}_Event.log', "a", encoding='utf-8') as f:
        f.write(f"\n{json.dumps(data, ensure_ascii=False)}")
        f.close()
    socketio.emit('event_list', {'data' : data}, namespace="/send_event")

#<-------------------------------------------------------Process logics----------------------------------------------------------->

def del_info(name, permit, flag, data):
    
    if data == "" or data == "\n":
        return
    time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    date = datetime.now().strftime('%Y-%m-%d')
    
    msg = None
    f_path = None
    info = None
    change = None
    
    if flag == "account":
        f_path = f"{USER_PATH}/data/UserData/UserTable"
        msg = "Delete Account"
        dname, did = data[0].split(":")
        dpermit = data[1]
        data = data[0]
        value = f"{time}\n{name} has deleted their Account\nUser: {name}\nUser Permit: {permit}\n\nDelete Account\nName: {dname}\nID: {did}\nPermit: {dpermit}\n\nDate: {date} {time}"
         
    elif flag == "ip":
        f_path = f"{USER_PATH}/data/AccessList/Access_list.csv"
        msg = "Delete IP"
        value = f"{name} Deleted {data} to the White List\nUser: {name}\nUser Permit : {permit}\n\nDelete White List : {data}\nDate : {date} {time}"
                
    elif flag == "rule":
        f_path = f"{USER_PATH}/data/offensive/rule"
        msg = "Delete Rule"
        value = f"{name} Added rule\nUser: {name}\nUser Permit: {permit}\nRule value: {data}\n\nDate: {date} {time}"
        
    with open(f_path, 'r') as f:
        info = f.readlines()
        f.close()
        
    for del_data in info:
        if data in del_data:
            info.remove(del_data)
            change = True
            
    if change:
        with open(f_path, 'w') as f:
            for i, line in enumerate(info):
                line = line.strip()
                if line == "":
                    continue
                if i < len(info) - 1:
                    f.write(line + '\n')
                else:
                    f.write(line)

        event_io(time, "Event", msg, name, value)
    return change

def check_account(maker, maker_permit ,name, id, pw, permit):
    time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    date = datetime.now().strftime('%Y-%m-%d')
    
    users = []
    msg = None
    with open(f'{USER_PATH}/data/UserData/UserTable') as f:
        for line in f:
            user_data = line.strip().split(':')
            users.append(user_data[1])
        f.close()

    if id in users:
        msg= "이미 존재하는 아이디입니다."
    
    elif len(pw) < 12:
        msg= "비밀번호는 12자 이상으로 설정해야 합니다."
    
    elif id == pw:
        msg = "아이디와 비밀번호는 동일할 수 없습니다."
    
    elif permit == "Super" and maker_permit != "Super":
        msg = "권한이 부족합니다.Super 계정은 Super 권한만 생성 가능합니다."
    
    if not msg:
        pw = system.SHA_Encrypt(pw)
        with open(f'{USER_PATH}/data/UserData/UserTable', 'a') as f:
            f.write(f"\n#{name}:{id}:{pw}:{permit}")
            f.close()
        value = f"{time}\n{maker} has made an account\nMaker:{maker}\nMaker_pirmit: {maker_permit}\n\nNew Account\nName: {name}\nPermit: {permit}\n\nDate: {date} {time}"
        event_io(time,"Event","Add Account",maker,value)
    else:
        value = f"{time}\n{maker} has Failed to make an account\nMaker:{maker}\nMaker_pirmit: {maker_permit}\n\nName: {name}\nPermit: {permit}\nLog_msg: {msg}\n\nDate: {date} {time}"
        event_io(time,"Event","Failed",maker,value)
    return msg

def list_account():
    user_tables = []
    
    with open('data/UserData/UserTable', 'r') as file:
            f = file.read().split('\n')

    for data in f:
        if data.strip():
            info = data.split(":")
            name, user_id, user_passwd, permit = info
            name = name[1:]
            user_tables.append([name, user_id, user_passwd, permit])
    
    return user_tables[1:]

def check_rule(rule : str = None, input_rule : str = None, data : dict = None):
    try:
        src_ip, src_port, target, des_ip, des_port, layer = input_rule.split(" ")[:6]
        layer = layer.lower()[1:]
        print(src_ip, src_port, target, des_ip, des_port, layer)
    except ValueError as e:
        msg = f"잘못된 규칙 {e}"
        return msg
    
    msg = None
    try:
        src_ip = "0.0.0.0" if src_ip == "any" else src_ip
        des_ip = "0.0.0.0" if des_ip == "any" else des_ip
        src_port = None if src_port == "any" else int(src_port)
        des_port = None if des_port == "any" else int(des_port)
    except ValueError as e:
        msg = f"잘못된 규칙 {e}"
        return msg
    try:
        ipaddress.ip_address(src_ip)
        ipaddress.ip_address(des_ip)
    except ValueError:
        msg = "IP address Error"

    if not (target == "-"):
        msg = "Target Error"

    if not ((src_port is None or (0 <= src_port <= 65535)) and (des_port is None or (0 <= des_port <= 65535))):
        msg = "Port range Error"

    if not ("layer" in layer or "protocol" in layer or "content" in layer):
        msg = "in missing layer or protocol"

    if msg:
        return msg
    else:
        add_rule_list(rule=rule, input_rule=input_rule)
     
import psutil
def hw_info():
    while True:
        net1 = psutil.net_io_counters()
        cpu = psutil.cpu_percent(interval=1)
        net2 = psutil.net_io_counters()
        mem = psutil.virtual_memory()
        
        bytes_sent = net2.bytes_sent - net1.bytes_sent
        bytes_recv = net2.bytes_recv - net1.bytes_recv
        total_bytes = bytes_sent + bytes_recv
        total_mb = total_bytes / (1024)
        
        
        used_gb = mem.used / (1024**3)
        total_gb = mem.total / (1024**3)
        
        data = {
            "cpu" : cpu,
            "mem" : f"{used_gb:.2f}/{total_gb:.2f}",
            "net" : f"{total_mb:.2f}"
        }
        socketio.emit('send_hw_info', {'data' : data})
    
def add_rule_list(rule, input_rule):
    with open("data/offensive/rule", 'a') as f:
        f.write(f"\n{rule} {input_rule}")
    network_utils.init_memory()
        
@system.system_event(log_type="system")
def app_thread():
    app.run(host='0.0.0.0', threaded=True ,port=8000)

@system.system_event(log_type="system") 
def packet_thread():
    while True:
        network_utils.get_packet(socketio.emit, event_io)

#<-------------------------------------------------------Management Main----------------------------------------------------------->

@system.system_event(log_type="system")
def main():
    try:
        packet_proccess = threading.Thread(target=packet_thread, daemon=True)
        packet_proccess.start()
        
        app_process = threading.Thread(target=app_thread)
        app_process.start()
        
        send_hw_info = threading.Thread(target=hw_info)
        send_hw_info.start()
    
    except KeyboardInterrupt:
        return f"Application stopped due to (Ctrl + C)"
    
    except SystemExit as e:
        return f"Application stopped {e})"
    
    except Exception as e:
        return f"Application stopped due to error: {e}"

if __name__ == '__main__':
    main()
    network_utils.init_memory()

    