
//Socket IO
//{ cpu: 15.7, mem: "3.19/7.71 GB", net: "0.00 MB/s" }
const socket = io();
socket.on('send_hw_info', (msg) => {
    console.log(msg.data);

    let cpu = Number(msg.data['cpu']);
    let mem = msg.data['mem'];
    let net = Number(msg.data['net']);  // 숫자로 변환 (혹시 모르니 안전하게)

    console.log(cpu, mem, net);

    // CPU/RAM UI 업데이트
    const cpu_el = document.getElementById('cpu_usage');
    const mem_el = document.getElementById('mem_usage');
    cpu = cpu.toFixed(1).padStart(5, ' ');
    cpu_el.textContent = `CPU: ${cpu}%`;
    mem_el.textContent = `RAM : ${mem}`;

    // === 차트에 net 데이터 추가 ===
    const now = new Date();
    const label = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    const chart = window.chart;
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(net);

    // x축을 최신 데이터 기준으로 이동
    const total = chart.data.labels.length;
    chart.options.scales.x.min = Math.max(0, total - MAX_VIEW);
    chart.options.scales.x.max = total - 1;

    chart.update();
});

socket.on('send_packet', (msg) => {
    const raw_data = msg.data;
    let json_data = raw_data;
    let SIP, DIP, PROTOCOL,PORT, LENGTH
    try{
        var packet_data = JSON.parse(json_data);
        if(Object.keys(packet_data)[1] === "Layer IP"){
            SIP = packet_data["Layer IP"]["Source Address"];
            DIP = packet_data["Layer IP"]["Destination Address"]
            PROTOCOL =  packet_data["Layer IP"]["Protocol"].split(" ")[1];
            PORT = packet_data["Layer " + PROTOCOL]["Destination Port"];
            LENGTH = new TextEncoder();
            LENGTH = LENGTH.encode(json_data).length;
        }
        else{
            PROTOCOL = Object.keys(packet_data)[1].split(" ")[1];
            allValues = packet_data["Layer "+PROTOCOL];

            SIP = Object.entries(allValues).filter(
            ([key, value]) => key.toLowerCase().includes('sender ip') || key.toLowerCase().includes('source')
            ).map(([key, value]) => value);

            DIP = Object.entries(allValues).filter(
            ([key, value]) => key.toLowerCase().includes('Destination')).map(([key, value]) => value);

            PORT = null;
            LENGTH = new TextEncoder();
            LENGTH = LENGTH.encode(json_data).length;

            if (SIP === undefined) {
                SIP = null;
            }
        }
    }
    catch(e){
        return;
    }
    updatePacketDisplay(SIP,DIP,PROTOCOL,PORT,LENGTH, packet_data);
});

function updatePacketDisplay(sip, dip, protocol, port, Length, packet_data) {

    let SIP, DIP,PROTOCOL,PORT,LENGTH;
    SIP = sip;
    DIP = dip;
    PROTOCOL = protocol;
    PORT = port;
    LENGTH = Length;
    packet_data = packet_data;

    const dataElement = document.getElementById("packet_data");
    const newDiv = document.createElement('div');
    newDiv.className = "data_table";
    newDiv.style.backgroundColor = "#e0e0e0";
    
    if(protocol === "ICMP"){
        newDiv.style.backgroundColor = "#e8e9a8";
    }

    const sipdiv = document.createElement('div');
    const dipdiv = document.createElement('div');
    const portdiv = document.createElement('div');
    const protocoldiv = document.createElement('div');
    const lengthdiv = document.createElement('div');

    sipdiv.textContent = SIP;
    dipdiv.textContent = DIP;
    portdiv.textContent = PORT;
    protocoldiv.textContent = PROTOCOL;
    lengthdiv.textContent = LENGTH;

    sipdiv.className = "name_tables";
    dipdiv.className = "name_tables";
    portdiv.className = "name_tables";
    protocoldiv.className = "name_tables";
    lengthdiv.className = "name_tables";

    newDiv.append(sipdiv, dipdiv, portdiv, protocoldiv, lengthdiv);
    dataElement.appendChild(newDiv);

    newDiv.addEventListener("click", function () {
        const newWindow = window.open("", "_blank", "width=600,height=600");
        if (newWindow) {
            const formattedText = formatPacketData(packet_data);
            newWindow.document.write(`
<html>
<head>
<title>Packet Detail</title>
<style>
                    body { font-family: monospace; white-space: pre-wrap; background: #f4f4f4; padding: 1em; color: #333; }
                    h2 { color: #0f4c81; }
</style>
</head>
<body>
<h2>패킷 상세 정보</h2>
<pre>${formattedText}</pre>
</body>
</html>
            `);
            newWindow.document.close();
        } else {
            alert("팝업 차단이 되어 있어 새 창을 열 수 없습니다.");
        }
    });
}
 
function formatPacketData(packet_data) {
    let result = "";
    for (const layer in packet_data) {
        // 레이어 이름 포맷팅 (예: "Layer ETH" → "ETH Layer")
        const layerName = layer.replace("Layer ", "") + " Layer";
        result += `\n ${layerName}\n`;
 
        // 각 필드 처리
        for (const [key, value] of Object.entries(packet_data[layer])) {
            // 특수문자 포함된 키 생략 (예: ".... ..0. .... .... .... ....")
            if (/[•\d.]/.test(key.trim())) continue;
 
            // 키 이름 포맷팅 (예: "SourcePort" → "Source Port")
            const formattedKey = key
                .replace(/([A-Z])/g, ' $1') // CamelCase 분리
                .replace(/^ /, '') // 맨 앞 공백 제거
                .replace(/Port$/, ' Port'); // Port 접미사 강제 추가
 
            result += `  ${formattedKey}: ${value}\n`;
        }
    }
    return result;
}

const socket_event = io('/send_event');

socket_event.on('connect', ()=>{
    socket_event.emit('request_data');
})

socket_event.on('event_list', (msg) =>{
    let time = msg.data["time"];
    let Type = msg.data["Type"];
    let Msg = msg.data["msg"];
    let user = msg.data["user"];
    let value = msg.data['value'];
    console.log(time,Type, Msg, user, value)
    updateEventDisplay(time,Type, Msg, user, value);
})

function updateEventDisplay(time,Type, Msg, user, value){

    const dataElement = document.getElementById("event_data");
    const newDiv = document.createElement('div');
    newDiv.className = "data_table";
    newDiv.style.backgroundColor = "#e0e0e0";

    const sipdiv = document.createElement('div');
    const dipdiv = document.createElement('div');
    const portdiv = document.createElement('div');
    const protocoldiv = document.createElement('div');
    const lengthdiv = document.createElement('div');

    sipdiv.textContent = time;
    dipdiv.textContent = Type;
    portdiv.textContent = Msg;
    protocoldiv.textContent = user;
    lengthdiv.textContent = "내용 확인";

    sipdiv.className = "name_tables";
    dipdiv.className = "name_tables";
    portdiv.className = "name_tables";
    protocoldiv.className = "name_tables";
    lengthdiv.className = "name_tables";

    if(Type === "Detect"){
        newDiv.style.backgroundColor = "#f89090";
    }

    newDiv.append(sipdiv, dipdiv, portdiv, protocoldiv, lengthdiv);
    dataElement.appendChild(newDiv);

    newDiv.addEventListener("click", function () {
        const newWindow = window.open("", "_blank", "width=600,height=600");

        if (newWindow) {;
            newWindow.document.body.style.backgroundColor = "#0f4c81";
            const pre = newWindow.document.createElement("div");
            pre.style = "white-space: pre;";
            pre.style.color = "white";
            pre.textContent=value;

            newWindow.document.body.appendChild(pre);
        } else {
            alert("팝업 차단이 되어 있어 새 창을 열 수 없습니다.");
        }
    });
}
let MAX_VIEW = 10; // 한 번에 보이는 데이터 개수
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('dataChart').getContext('2d');

    // 초기 데이터 생성 - 빈 상태
    const labels = [];
    const data = [];

    // 마우스 휠 스크롤 처리 커스텀 이벤트 핸들러
    function wheelHandler(e) {
        e.preventDefault();

        const delta = e.deltaY > 0 ? 1 : -1; // 휠 방향 감지
        const step = 2; // 스크롤 스텝 크기

        const minIndex = chart.options.scales.x.min ?? 0;
        const maxIndex = chart.options.scales.x.max ?? (chart.data.labels.length - 1);

        const newMin = Math.max(0, minIndex + delta * step);
        const newMax = Math.min(chart.data.labels.length - 1, maxIndex + delta * step);

        if (newMax - newMin >= 5 && newMin >= 0 && newMax < chart.data.labels.length) {
            chart.options.scales.x.min = newMin;
            chart.options.scales.x.max = newMax;
            chart.update();
        }
    }

    // 차트 생성 (min, max 제거)
    window.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '데이터 크기 (kb/s)',
                data: data,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 300,
                easing: 'easeOutQuad'
            },
            scales: {
                x: {
                    title: { display: true, text: '시간 (시:분:초)' }
                    // min, max 설정 제거
                },
                y: {
                    min: 0,
                    max: 5000,
                    ticks: { stepSize: 500 },
                    title: { display: true, text: '데이터 크기 (byte)' }
                }
            }
        }
    });

    ctx.canvas.addEventListener('wheel', wheelHandler, { passive: false });

    // resetZoom 함수 (실시간 데이터 수에 따라 동적 설정)
    window.resetZoom = function() {
        const total = chart.data.labels.length;
        chart.options.scales.x.min = Math.max(0, total - MAX_VIEW);
        chart.options.scales.x.max = total - 1;
        chart.update();
    };
});

