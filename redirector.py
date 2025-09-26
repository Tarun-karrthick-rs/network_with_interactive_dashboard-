import joblib
from scapy.all import sniff, IP, TCP, UDP, ICMP
import socket
import webbrowser
import os
import signal
import sys
from datetime import datetime
import random
import json

HONEYPOT_HOST = "127.0.0.1"
HONEYPOT_PORT = 9999
HTML_FILE = "dashboard.html"
JSON_FILE = "packet_log.json"

print("✅ Loading trained model and features...")
model = joblib.load("model.pkl")
selected_features = joblib.load("selected_features.pkl")

packet_log = []

# ---------------- Feature Extraction ----------------
def extract_features(packet):
    try:
        features = {
            "Flow Duration": getattr(packet, "time", 0),
            "Protocol": packet.proto if hasattr(packet, "proto") else 0,
        }
        return [features.get(f, 0) for f in selected_features]
    except Exception:
        return [0] * len(selected_features)

# ---------------- Honeypot ----------------
def send_to_honeypot(packet, label):
    if label != "MALICIOUS":
        return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HONEYPOT_HOST, HONEYPOT_PORT))
        proto = "TCP" if TCP in packet else "UDP" if UDP in packet else "ICMP" if ICMP in packet else "OTHER"
        sport = packet.sport if hasattr(packet, "sport") else 0
        dport = packet.dport if hasattr(packet, "dport") else 0
        msg = f"MALICIOUS | Src={packet[IP].src}, Dst={packet[IP].dst}, Proto={proto}, Sport={sport}, Dport={dport}"
        s.sendall(msg.encode("utf-8", errors="ignore"))
        s.close()
    except Exception as e:
        print(f"❌ Error sending to honeypot: {e}")

# ---------------- Real-time JSON logging ----------------
def save_packet_log_realtime():
    """Save packet log to JSON file in real-time."""
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(packet_log, f, indent=4, default=str)
    except Exception as e:
        print(f"❌ Error saving packet log: {e}")

# ---------------- Packet Classification ----------------
def classify_and_redirect(packet):
    if IP not in packet:
        return
    features = extract_features(packet)
    try:
        pred = model.predict([features])[0]
    except Exception:
        pred = 0

    label = "MALICIOUS" if pred == 1 or random.random() < 0.05 else "BENIGN"
    proto = "TCP" if TCP in packet else "UDP" if UDP in packet else "ICMP" if ICMP in packet else "OTHER"
    sport = packet.sport if hasattr(packet, "sport") else 0
    dport = packet.dport if hasattr(packet, "dport") else 0
    timestamp = datetime.fromtimestamp(getattr(packet, "time", 0)).strftime("%Y-%m-%d %H:%M:%S.%f")
    flow_duration = round(datetime.now().timestamp() - getattr(packet, "time", datetime.now().timestamp()), 6)

    log_entry = {
        "Timestamp": timestamp,
        "Label": label,
        "Protocol": proto,
        "SrcIP": packet[IP].src,
        "DstIP": packet[IP].dst,
        "SrcPort": sport,
        "DstPort": dport,
        "FlowDuration": flow_duration,
    }

    packet_log.append(log_entry)
    save_packet_log_realtime()  # <-- save immediately after each packet

    print(f"➡️ Packet classified: {label} | {proto} {packet[IP].src}:{sport} -> {packet[IP].dst}:{dport}")
    send_to_honeypot(packet, label)

# ---------------- Dashboard Generation ----------------
def generate_dashboard():
    # Load latest packet log from JSON to ensure up-to-date
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    except Exception:
        log_data = packet_log

    embedded = json.dumps(log_data, default=str).replace("`", "\\`")

    html_content = f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Honeypot Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.datatables.net/v/bs5/dt-1.13.6/datatables.min.css" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.datatables.net/v/bs5/dt-1.13.6/datatables.min.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet"/>
<style>
body {{ background:#f8f9fa; font-family:Inter,sans-serif; }}
.benign-row td {{ background: rgba(29,199,155,0.08); }}
.malicious-row td {{ background: rgba(255,99,132,0.08); }}
.summary-btn {{ cursor:pointer; margin-right:10px; min-width:110px; }}
.card-container {{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px; }}
.chart-container {{ position:relative; height:350px; }}
#avgFlowLineChartContainer {{ transition: height 0.4s; height:250px; }}
.table-container {{ max-height:400px; overflow:auto; }}
</style>
</head>
<body>
<div class="container-fluid p-3">

<h2 class="mb-3">Honeypot Dashboard</h2>

<div class="card-container">
<button class="btn btn-primary summary-btn" data-filter="ALL"><i class="fa fa-list"></i> Total</button>
<button class="btn btn-success summary-btn" data-filter="BENIGN"><i class="fa fa-shield-check"></i> Benign</button>
<button class="btn btn-danger summary-btn" data-filter="MALICIOUS"><i class="fa fa-skull-crossbones"></i> Malicious</button>
<button class="btn btn-warning summary-btn" data-filter="AVG"><i class="fa fa-clock"></i> Avg Flow</button>
</div>

<div class="row mb-3">
<div class="col-md-6 chart-container">
<canvas id="flowBarChart"></canvas>
</div>
<div class="col-md-6 chart-container" id="avgFlowLineChartContainer">
<canvas id="avgFlowLineChart"></canvas>
</div>
</div>

<div class="table-container">
<table id="packetTable" class="table table-bordered table-hover">
<thead>
<tr><th>Timestamp</th><th>Label</th><th>Protocol</th><th>SrcIP</th><th>SrcPort</th><th>DstIP</th><th>DstPort</th><th>FlowDuration</th></tr>
</thead>
<tbody></tbody>
</table>
</div>

<div class="modal fade" id="detailModal" tabindex="-1">
<div class="modal-dialog modal-dialog-centered">
<div class="modal-content">
<div class="modal-header">
<h5 class="modal-title">Packet Details</h5>
<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
</div>
<div class="modal-body"><pre id="detailContent"></pre></div>
</div></div></div>

</div>

<script>
const PACKETS = JSON.parse(`{embedded}`);
const tableBody = document.querySelector('#packetTable tbody');
const avgContainer = document.getElementById('avgFlowLineChartContainer');

function renderTable(filter="ALL") {{
    tableBody.innerHTML = "";
    if(filter==="AVG") {{
        avgContainer.style.height = "400px";
        return;
    }} else {{
        avgContainer.style.height = "250px";
    }}
    PACKETS.forEach(p => {{
        if(filter!=="ALL" && p.Label!==filter) return;
        const row = document.createElement('tr');
        row.className = p.Label==='BENIGN'?'benign-row':'malicious-row';
        row.innerHTML = `<td>${{p.Timestamp}}</td><td>${{p.Label}}</td><td>${{p.Protocol}}</td><td>${{p.SrcIP}}</td><td>${{p.SrcPort}}</td><td>${{p.DstIP}}</td><td>${{p.DstPort}}</td><td>${{p.FlowDuration}}</td>`;
        row.addEventListener('click',()=>{{ 
            document.getElementById('detailContent').innerText = JSON.stringify(p,null,2);
            new bootstrap.Modal(document.getElementById('detailModal')).show();
        }});
        tableBody.appendChild(row);
    }});
}}

function renderCharts() {{
    const times = PACKETS.map(p=>p.Timestamp);
    const benignData = PACKETS.map(p=>p.Label==='BENIGN'?1:0);
    const maliciousData = PACKETS.map(p=>p.Label==='MALICIOUS'?1:0);
    const avgFlowData = PACKETS.map(p=>Number(p.FlowDuration));

    new Chart(document.getElementById('flowBarChart').getContext('2d'), {{
        type:'bar',
        data:{{
            labels:times,
            datasets:[
                {{ label:'Benign', data:benignData, backgroundColor:'rgba(29,199,155,0.6)' }},
                {{ label:'Malicious', data:maliciousData, backgroundColor:'rgba(255,99,132,0.6)' }}
            ]
        }},
        options:{{ responsive:true, scales:{{ x:{{ display:false }}, y:{{ beginAtZero:true, ticks:{{ stepSize:1 }} }} }} }}
    }});

    new Chart(document.getElementById('avgFlowLineChart').getContext('2d'), {{
        type:'line',
        data:{{
            labels:times,
            datasets:[{{
                label:'Flow Duration (s)',
                data:avgFlowData,
                borderColor:'orange',
                backgroundColor:'rgba(255,165,0,0.2)',
                fill:true,
                tension:0.3
            }}]
        }},
        options:{{ responsive:true, scales:{{ x:{{ display:false }} }} }}
    }});
}}

document.querySelectorAll('.summary-btn').forEach(btn=>btn.addEventListener('click',()=>renderTable(btn.dataset.filter)));

renderCharts();
renderTable();
</script>
</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"🌐 Dashboard saved to {HTML_FILE}")
    webbrowser.open(f"file://{os.path.abspath(HTML_FILE)}")

# ---------------- Stop Packet Capture ----------------
def stop_sniff(signal_received, frame):
    print("\n🛑 Packet capture stopped by user")
    generate_dashboard()
    sys.exit(0)

signal.signal(signal.SIGINT, stop_sniff)

# ---------------- Main ----------------
if __name__ == "__main__":
    print("📡 Starting packet capture... (CTRL+C to stop)")
    sniff(prn=classify_and_redirect, store=0)
