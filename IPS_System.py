from flask import Flask, render_template, Response, request
from collections import deque
from module import network_utils, system_utils
import threading

packet_queue = deque()
event_queue = deque()

app = Flask(__name__)
system = system_utils


#<--------------------------------------------------------Web Service------------------------------------------------------------>

@app.before_request
@system.log_event(log_type="access")
def accses_ctl():
    with open("data/Access_list", 'r') as Access_list:
        Access_list = Access_list.read().split()
        if request.remote_addr not in Access_list:
            return render_template('block.html')
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_packet')
def sending_packet():
    return Response(pop_queue(), content_type='text/event-stream')

#<-------------------------------------------------------Process logics----------------------------------------------------------->

def pop_queue():
    global packet_queue
    while True:
        if len(packet_queue):
            data = packet_queue.popleft()
            yield f"data: {[str(data)]}\n\n"

#<-------------------------------------------------------Thread Process----------------------------------------------------------->

@system.log_event(log_type="system")
def app_thread():
    app.run(host='0.0.0.0', threaded=True ,port=8000)

@system.log_event(log_type="system") 
def packet_thread():
    global packet_queue
    while True:
        data = network_utils.get_packet()
        packet_queue.append(data)

#<-------------------------------------------------------Management Main----------------------------------------------------------->

@system.log_event(log_type="system")
def main():
    try:
        packet_proccess = threading.Thread(target=packet_thread, daemon=True)
        packet_proccess.start()
        
        app_process = threading.Thread(target=app_thread)
        app_process.start()
    
    except KeyboardInterrupt:
        return f"Application stopped due to (Ctrl + C)"
    
    except SystemExit as e:
        return f"Application stopped {e})"
    
    except Exception as e:
        return f"Application stopped due to error: {e}"

if __name__ == '__main__':
    main()