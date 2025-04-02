from flask import Flask, render_template, Response, request
from collections import deque
import detection_offensive
import get_sysinfo
import threading
import time


packet_queue = deque()
event_queue = deque()

input_trigger = False

app = Flask(__name__)
        
#<--------------------------------------------------------Web Service------------------------------------------------------------>

@app.before_request
def acsses_ctl():
    with open("data/Access_list", 'r') as Access_list:
        Access_list = Access_list.read().split()
        if request.remote_addr not in Access_list:
            return render_template('block.html')
        
@app.route('/')
def index():
    global input_trigger
    input_trigger= True
    return render_template('index.html')

@app.route('/send_packet')
def sending_packet():
    data = pop_queue()
    print("dwadawdawdawdaw",data) # <generator object pop_queue at 0x7222bebdd5b0>
    return Response(data, content_type='text/event-stream')

#<-------------------------------------------------------Process logics----------------------------------------------------------->

def pop_queue():
    global packet_queue
    while True:
        if len(packet_queue):
            data = packet_queue.popleft()
            yield f"data: {[str(data)]}\n\n"

#<-------------------------------------------------------Thread Process----------------------------------------------------------->

def packet_thread():
    global packet_queue
    global input_trigger
    while True:
        data = detection_offensive.get_packet()
        if input_trigger:
            packet_queue.append(data)

#<-------------------------------------------------------Management Main----------------------------------------------------------->

if __name__ == '__main__':
    packet_proccess = threading.Thread(target=packet_thread, daemon=True)
    packet_proccess.start()
    
    app.run(host='0.0.0.0', threaded = True ,port=8000)