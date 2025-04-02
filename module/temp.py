from flask import Flask, render_template, Response, request
import threading
import time
import detection_offensive
import json
from collections import deque

app = Flask(__name__)

white_list = ['127.0.0.1']

#<-----------------------------------------------------Packet Process------------------------------------------------------------>

def detection(data : json):
    pass

def collect_data():
    data = detection_offensive.get_packet()
    return data

def packet_capture():
    while True:
        data = detection_offensive.get_packet()
        yield f"data: {[str(data)]}\n\n"
        
@app.route('/send_packet')
def sse():
    return Response(packet_capture(), content_type='text/event-stream')
        
        
#<--------------------------------------------------------Web service------------------------------------------------------------>

#White list 
@app.before_request
def acsses_ctl():
    if request.remote_addr not in white_list: 
        return render_template('block.html')


@app.route('/')
def index():
    print(request.remote_addr)
    return render_template('index.html')

#<---------------------------------------------------------Threading------------------------------------------------------------->


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded = True)
#help me.... I sick my brain..