
//Socket IO
const socket = io();
socket.on('send_hw_info', (msg) => {
    console.log(msg.data);
    cpu = msg.data['cpu'];
    mem = msg.data['mem'];
    net = msg.data['net'];
    console.log(cpu, mem, net);
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

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('dataChart').getContext('2d');
    const MAX_VIEW = 10; // 한 번에 보이는 데이터 개수
    const TOTAL_DATA = 50; // 시작 데이터 개수

    // 초기 데이터 생성
    const labels = [];
    const data = [];
    const now = new Date();
    for (let i = 0; i < TOTAL_DATA; i++) {
        const t = new Date(now.getTime() - (TOTAL_DATA - i - 1) * 3000);
        labels.push(
            `${t.getHours()}:${t.getMinutes().toString().padStart(2, '0')}:${t.getSeconds().toString().padStart(2, '0')}`
        );
        data.push(Math.floor(Math.random() * 2000));
    }

    // 마우스 휠 스크롤 처리 커스텀 이벤트 핸들러
    function wheelHandler(e) {
        // 휠 이벤트 방지
        e.preventDefault();
        
        const delta = e.deltaY > 0 ? 1 : -1; // 휠 방향 감지
        const step = 2; // 스크롤 스텝 크기
        
        // 현재 x축 범위
        const minIndex = chart.options.scales.x.min;
        const maxIndex = chart.options.scales.x.max;
        
        // 새 범위 계산 (휠 방향에 따라 좌우로 이동)
        const newMin = Math.max(0, minIndex + delta * step);
        const newMax = Math.min(chart.data.labels.length - 1, maxIndex + delta * step);
        
        // 범위가 유효하면 적용
        if (newMax - newMin >= 5 && newMin >= 0 && newMax < chart.data.labels.length) {
            chart.options.scales.x.min = newMin;
            chart.options.scales.x.max = newMax;
            chart.update();
        }
    }

    // 차트 생성
    window.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '데이터 크기 (byte)',
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
                    title: { display: true, text: '시간 (시:분:초)' },
                    min: TOTAL_DATA - MAX_VIEW, // 처음에는 오른쪽 10개만 보이게
                    max: TOTAL_DATA - 1 
                },
                y: {
                    min: 0,
                    max: 2000,
                    ticks: { stepSize: 200 },
                    title: { display: true, text: '데이터 크기 (byte)' }
                }
            }
        }
    });
    
    // 캔버스에 마우스 휠 이벤트 리스너 추가
    ctx.canvas.addEventListener('wheel', wheelHandler, { passive: false });

    // 랜덤 간격으로 데이터 추가 (1~5초)
    /*function addRandomData() {
        const t = new Date();
        const newLabel = `${t.getHours()}:${t.getMinutes().toString().padStart(2, '0')}:${t.getSeconds().toString().padStart(2, '0')}`;
        const newValue = Math.floor(Math.random() * 2000);

        chart.data.labels.push(newLabel);
        chart.data.datasets[0].data.push(newValue);

        // 자동 스크롤하려면 다음 줄 주석 해제
        chart.options.scales.x.min++;
        chart.options.scales.x.max++;

        chart.update();

        const nextInterval = Math.floor(Math.random() * 5 + 1) * 1000;
        setTimeout(addRandomData, nextInterval);
    }
    addRandomData();
*/
    // 초기 위치로 되돌리기
    window.resetZoom = function() {
        const total = chart.data.labels.length;
        chart.options.scales.x.min = Math.max(0, total - MAX_VIEW);
        chart.options.scales.x.max = total - 1;
        chart.update();
    };
});
