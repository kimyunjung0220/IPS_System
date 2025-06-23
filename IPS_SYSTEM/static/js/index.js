// 전역 변수 초기화
let allPackets = [];
let currentFilter = "";
let allEvents = [];
let currentEventFilter = "";
let userInteracting = false;
let autoReturnTimer = null;

document.addEventListener('DOMContentLoaded', function() {
    // Socket: Hardware 정보 갱신
    const socket = io();
    
    socket.on('send_hw_info', (msg) => {
    const cpu = Number(msg.data.cpu);
    const mem = msg.data.mem;
    const net = Number(msg.data.net);  // 문자열이지만 숫자 변환 가능

    document.getElementById('cpu_usage').innerText = `CPU 사용량: ${cpu.toFixed(1)}%`;
    document.getElementById('mem_usage').innerText = `MEM 사용량: ${mem}`;

    if (!isNaN(net)) {
        chart.data.labels.push(new Date().toLocaleTimeString());
        chart.data.datasets[0].data.push(net);

        const total = chart.data.labels.length;

        if (!userInteracting) {
            chart.options.scales.x.min = Math.max(0, total - MAX_VIEW);
            chart.options.scales.x.max = total - 1;
        }
        chart.update();
    } else {
        console.warn("수신된 net 값이 NaN입니다:", msg.data.net);
    }
});

// 패킷 목록 검색 기능
document.getElementById('applyPacketFilter').addEventListener('click', function() {
    const filterValue = document.getElementById('packetFilter').value.trim().toUpperCase();
    const parentDiv = document.getElementById('packet_data');
    const rowDivs = parentDiv.getElementsByClassName('packet-row'); // 반드시 row 단위

    for (let i = 0; i < rowDivs.length; i++) {
        // row 전체의 텍스트를 합쳐서 필터링
        const text = rowDivs[i].innerText.toUpperCase();
        if (!filterValue) {
            rowDivs[i].style.display = 'flex'; // flex로 설정
        } else {
            if (text.indexOf(filterValue) > -1) {
                rowDivs[i].style.display = 'flex';
            } else {
                rowDivs[i].style.display = 'none';
            }
        }
    }
});

// 이벤트 목록 검색 기능
document.getElementById('applyEventFilter').addEventListener('click', function() {
    const filterValue = document.getElementById('eventFilter').value.trim().toUpperCase();
    const parentDiv = document.getElementById('event_data');
    const rowDivs = parentDiv.getElementsByClassName('event-row');

    for (let i = 0; i < rowDivs.length; i++) {
        const text = rowDivs[i].innerText.toUpperCase();
        if (!filterValue) {
            rowDivs[i].style.display = 'flex';
        } else {
            if (text.indexOf(filterValue) > -1) {
                rowDivs[i].style.display = 'flex';
            } else {
                rowDivs[i].style.display = 'none';
            }
        }
    }
});




    socket.on('send_packet', (msg) => {
    let packetData = msg.data;
    let parsedData;

    try {
        parsedData = JSON.parse(packetData);
    } catch (e) {
        console.error("JSON 파싱 실패:", e);
        return;
    }

    let SIP = "-", DIP = "-", PROTOCOL = "-", PORT = "-", LENGTH = "-";

    try {
        if (Object.keys(parsedData)[1] === "Layer IP") {
            SIP = parsedData["Layer IP"]["Source Address"];
            DIP = parsedData["Layer IP"]["Destination Address"];
            PROTOCOL = parsedData["Layer IP"]["Protocol"].split(" ")[1];
            PORT = parsedData["Layer " + PROTOCOL]?.["Destination Port"] || "-";
        } else {
            PROTOCOL = Object.keys(parsedData)[1].split(" ")[1];
            let layerData = parsedData["Layer " + PROTOCOL];
            SIP = Object.entries(layerData).find(([k]) => k.toLowerCase().includes("sender ip") || k.toLowerCase().includes("source"))?.[1] || "-";
            DIP = Object.entries(layerData).find(([k]) => k.toLowerCase().includes("destination"))?.[1] || "-";
            PORT = "-";
        }

        LENGTH = new TextEncoder().encode(packetData).length;
    } catch (e) {
        console.error("패킷 파싱 중 오류:", e);
        return;
    }

    // 전체 패킷 저장
    const packet = { sip: SIP, dip: DIP, protocol: PROTOCOL, port: PORT, length: LENGTH, raw: parsedData };
    allPackets.push(packet);
    
    // 필터 조건 충족 시만 화면에 출력
    if (!currentFilter || PROTOCOL.toLowerCase().includes(currentFilter)) {
        updatePacketDisplay(SIP, DIP, PROTOCOL, PORT, LENGTH, parsedData);
    }
});

});

function updatePacketDisplay(sip, dip, protocol, port, length, packet_data) {
    const dataElement = document.getElementById("packet_data");
    const rowDiv = document.createElement('div');
    rowDiv.className = "packet-row";
    if (protocol === "ICMP") rowDiv.style.backgroundColor = "#e8e9a8";

    // 각 필드를 셀로 분리
    const sipDiv = document.createElement('div');
    sipDiv.className = "packet-cell";
    sipDiv.textContent = sip;

    const dipDiv = document.createElement('div');
    dipDiv.className = "packet-cell";
    dipDiv.textContent = dip;

    const portDiv = document.createElement('div');
    portDiv.className = "packet-cell";
    portDiv.textContent = port;

    const protocolDiv = document.createElement('div');
    protocolDiv.className = "packet-cell";
    protocolDiv.textContent = protocol;

    const lengthDiv = document.createElement('div');
    lengthDiv.className = "packet-cell";
    lengthDiv.textContent = length;

    rowDiv.append(sipDiv, dipDiv, portDiv, protocolDiv, lengthDiv);
    dataElement.appendChild(rowDiv);

    rowDiv.addEventListener("click", function () {
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

function updateEventDisplay(time, Type, Msg, user, value) {
    const dataElement = document.getElementById("event_data");
    const rowDiv = document.createElement('div');
    rowDiv.className = "event-row";
    if (Type === "Detect") rowDiv.style.backgroundColor = "#f89090";

    const timeDiv = document.createElement('div');
    timeDiv.className = "event-cell";
    timeDiv.textContent = time;

    const typeDiv = document.createElement('div');
    typeDiv.className = "event-cell";
    typeDiv.textContent = Type;

    const msgDiv = document.createElement('div');
    msgDiv.className = "event-cell";
    msgDiv.textContent = Msg;

    const userDiv = document.createElement('div');
    userDiv.className = "event-cell";
    userDiv.textContent = user;

    const detailDiv = document.createElement('div');
    detailDiv.className = "event-cell";
    detailDiv.textContent = "내용 확인";

    rowDiv.append(timeDiv, typeDiv, msgDiv, userDiv, detailDiv);
    dataElement.appendChild(rowDiv);

    rowDiv.addEventListener("click", function () {
        const newWindow = window.open("", "_blank", "width=600,height=600");
        if (newWindow) {
            newWindow.document.body.style.backgroundColor = "#0f4c81";
            const pre = newWindow.document.createElement("div");
            pre.style = "white-space: pre;";
            pre.style.color = "white";
            pre.textContent = value;
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
        onUserPanOrZoom(); // 추가

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
    
// 팬/줌 이벤트 감지
function onUserPanOrZoom() {
    userInteracting = true;
    if (autoReturnTimer) clearTimeout(autoReturnTimer);
    autoReturnTimer = setTimeout(() => {
        userInteracting = false;
        moveToLatest();
    }, 5000);
}

// 최신 데이터로 이동
function moveToLatest() {
    const total = chart.data.labels.length;
    chart.options.scales.x.min = Math.max(0, total - MAX_VIEW);
    chart.options.scales.x.max = total - 1;
    chart.update();
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
                fill: false,
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
            },
            plugins: {
            zoom: {
                pan: { enabled: true, mode: 'x' },
                zoom: { enabled: true, mode: 'x' },
                onPan: onUserPanOrZoom,
                onZoom: onUserPanOrZoom
            }
        }
        }
    });

    ctx.canvas.addEventListener('wheel', wheelHandler, { passive: false });

});

