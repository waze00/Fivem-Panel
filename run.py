import os
import requests
from flask import Flask, render_template_string, url_for, request

app = Flask(__name__)

# --- SUNUCU TANIMLAMALARI ---
SERVERS = [
    {
        "id": "z5gxl9", 
        "name": "MDPVP", 
        "short_name": "MDPVP", 
        "logo": "mdpvp.gif",
        "primary_color": "#ff1d1d", 
        "accent_color": "#ffffff"
    },
    {
        "id": "z5rgx4", 
        "name": "WELLGUN 8.SEZON", 
        "short_name": "WELLGUN", 
        "logo": "wellgun.gif",
        "primary_color": "#ffffff", 
        "accent_color": "#ffffff"
    },
    {
        "id": "zrqlap", 
        "name": "LETRA X", 
        "short_name": "LETRA", 
        "logo": "letra.gif",
        "primary_color": "#1b5e8b", 
        "accent_color": "#ecf0f1"
    },
    {
        "id": "epx97a", 
        "name": "DADDY 1.0", 
        "short_name": "DADDY", 
        "logo": "daddy.png",
        "primary_color": "#cc2e2e", 
        "accent_color": "#ffffff"
    },
    {
        "id": "zem7ky", 
        "name": "GUID PVP 3.0", 
        "short_name": "GUID", 
        "logo": "guid.gif",
        "primary_color": "#beaf1f", 
        "accent_color": "#ffffff"
    },
]

# --- YÖNETİCİ BİLGİLERİ ---
WAZE_ID = "827593836229296188"
LILKNIFE_ID = "821434006843031624"

# --- HTML/CSS ŞABLONU ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ current_server.name }} | Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Audiowide&family=Inter:wght@400;700;900&family=Orbitron:wght@800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: {{ current_server.primary_color }};
            /* Izgara ve efektler için şeffaf renkler */
            --primary-rgb: {{ current_server.primary_color | replace('#', '') }}; /* Python tarafında hex-to-rgb dönüşümü yapılabilir ama şimdilik manuel % şeffaflık kullanacağız */
            --primary-grid: {{ current_server.primary_color }}26; /* %15 Opasite */
            --primary-glow: {{ current_server.primary_color }}0D; /* %5 Opasite */
            
            --accent: {{ current_server.accent_color }};
            --bg: #030305;
            --card: rgba(10, 10, 14, 0.96);
            --discord-blue: #5865F2;
            --sidebar-bg: rgba(5, 5, 8, 0.99);
        }
        
        body { margin: 0; background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; overflow-x: hidden; position: relative; min-height: 100vh; }
        
        /* --- YENİ GELİŞMİŞ ARKA PLAN --- */
        
        /* 1. Katman: Dinamik Renk Bulutu ve Tarama Çizgileri */
        body::before {
            content: ""; 
            position: fixed; 
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                /* Merkezden yayılan sunucu renginde hafif parlama */
                radial-gradient(circle at 50% 50%, var(--primary-glow) 0%, transparent 70%),
                /* Çok hafif yatay tarama çizgileri */
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);
            z-index: -2;
        }

        /* 2. Katman: Hareketli Cyberpunk Izgarası (Perspective Grid) */
        .bg-grid-container {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            perspective: 350px; /* 3D derinlik hissi */
            z-index: -1;
            overflow: hidden;
            opacity: 0.8;
        }

        .bg-grid {
            position: absolute;
            width: 200%; height: 200%; /* Ekranı kaplaması için büyük */
            top: -50%; left: -50%;
            background-image: 
                linear-gradient(var(--primary-grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--primary-grid) 1px, transparent 1px);
            background-size: 60px 60px;
            transform: rotateX(45deg); /* Yatay yatırma */
            animation: grid-flow 20s linear infinite; /* Hareket animasyonu */
            -webkit-mask-image: radial-gradient(circle, rgba(0,0,0,1) 10%, rgba(0,0,0,0) 70%);
            mask-image: radial-gradient(circle, rgba(0,0,0,1) 10%, rgba(0,0,0,0) 70%);
        }

        /* Izgara hareket animasyonu (yukarı doğru akış) */
        @keyframes grid-flow {
            from { transform: rotateX(45deg) translateY(0); }
            to { transform: rotateX(45deg) translateY(60px); } /* 1 birim kare kadar hareket ettir */
        }
        
        /* --- ARKA PLAN BİTİŞ --- */

        .sidebar {
            position: fixed; top: 0; left: -300px; width: 280px; height: 100%;
            background: var(--sidebar-bg); border-right: 1px solid var(--primary);
            z-index: 2000; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            padding: 30px 20px; box-shadow: 20px 0 50px rgba(0,0,0,0.8);
            backdrop-filter: blur(5px);
        }
        .sidebar.active { left: 0; }
        .sidebar-header { font-family: 'Orbitron'; color: var(--primary); font-size: 18px; margin-bottom: 30px; border-bottom: 1px solid var(--primary-grid); padding-bottom: 10px; }
        .server-item { 
            display: block; padding: 15px; margin-bottom: 10px; background: rgba(255,255,255,0.02);
            border-radius: 8px; text-decoration: none; color: #fff; font-family: 'Inter';
            transition: 0.3s;
        }
        .server-item:hover { background: var(--primary-grid); transform: translateX(5px); }
        .server-item.active { border: 1px solid var(--primary); background: var(--primary-glow); }
        
        .overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); display: none; z-index: 1999; backdrop-filter: blur(3px);
        }
        .overlay.active { display: block; }
        
        .navbar { 
            padding: 10px 5%; background: rgba(0, 0, 0, 0.95); 
            border-bottom: 2px solid var(--primary); display: flex; 
            justify-content: space-between; align-items: center; 
            position: sticky; top: 0; z-index: 1000;
            backdrop-filter: blur(5px);
        }
        .menu-btn { color: #fff; font-size: 24px; cursor: pointer; transition: 0.3s; padding: 5px 15px; border-radius: 5px; margin-right: 10px; }
        .menu-btn:hover { color: var(--primary); background: rgba(255,255,255,0.05); }
        .logo-box { display: flex; align-items: center; }
        .nav-logo { height: 60px; filter: drop-shadow(0 0 15px var(--primary)); transition: 0.5s ease; }
        .logo-text { font-family: 'Audiowide'; font-size: 26px; color: #fff; margin-left: 10px; }
        .current-tag { font-family: 'Orbitron'; font-size: 10px; color: var(--accent); margin-left: 10px; border: 1px solid var(--primary-grid); padding: 2px 6px; border-radius: 4px; }
        .discord-link { font-family: 'Orbitron'; color: #fff; text-decoration: none; font-size: 14px; font-weight: 800; transition: 0.3s; }
        .discord-link:hover { color: var(--discord-blue); text-shadow: 0 0 10px var(--discord-blue); }
        
        .container { width: 90%; max-width: 1200px; margin: 40px auto; position: relative; z-index: 1; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; padding: 10px; }
        .card { 
            background: var(--card); 
            border: 1px solid rgba(255,255,255,0.03); 
            border-radius: 15px; 
            padding: 30px 20px; 
            text-align: center; 
            transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            cursor: pointer; 
            position: relative; 
            overflow: hidden;
        }
        .card:hover { 
            border-color: var(--primary); 
            transform: translateY(-5px); 
            box-shadow: 0 10px 40px -10px var(--primary-grid);
        }
        
        /* Kartın arkasına hafif bir parlama efekti */
        .card::after {
            content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at center, var(--primary-glow) 0%, transparent 70%);
            opacity: 0; transition: 0.3s; z-index: -1;
        }
        .card:hover::after { opacity: 1; }
        
        .admin-name { font-family: 'Orbitron'; font-size: 30px; font-weight: 900; color: #fff; margin-bottom: 10px; display: block; text-shadow: 0 0 10px rgba(255,255,255,0.3); }
        .admin-img { width: 100px; height: 100px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.05); margin-bottom: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
        .player-val { font-family: 'Orbitron'; font-size: 55px; color: var(--accent); text-shadow: 0 0 25px var(--primary); font-weight: 900; }
        .label-small { color: #666; font-size: 10px; letter-spacing: 2px; font-weight: 800; margin-bottom: 5px; display: block; }
        
        .search-area { display: flex; gap: 10px; margin-bottom: 20px; }
        .search-input { flex-grow: 1; padding: 15px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; color: #fff; outline: none; transition: 0.3s; font-family: 'Inter'; }
        .search-input:focus { border-color: var(--primary); background: rgba(255,255,255,0.05); box-shadow: 0 0 15px var(--primary-glow); }
        .refresh-btn { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); color: #fff; padding: 15px; border-radius: 10px; cursor: pointer; transition: 0.3s; }
        .refresh-btn:hover { background: var(--primary); border-color: var(--primary); box-shadow: 0 0 15px var(--primary); }
        
        .table-wrap { background: var(--card); border-radius: 15px; overflow: hidden; border: 1px solid rgba(255,255,255,0.03); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        table { width: 100%; border-collapse: collapse; }
        th { background: rgba(0,0,0,0.4); padding: 18px 15px; text-align: left; color: var(--primary); font-family: 'Orbitron'; font-size: 11px; letter-spacing: 1px; border-bottom: 1px solid var(--primary-grid); }
        td { padding: 14px 15px; border-bottom: 1px solid rgba(255,255,255,0.01); font-size: 14px; transition: 0.2s; }
        tr:hover td { background: rgba(255,255,255,0.01); color: var(--accent); }
        
        #toast { 
            visibility: hidden; 
            min-width: 250px; 
            background-color: var(--primary); 
            color: {{ '#000' if current_server.id == 'z5rgx4' else '#fff' }}; 
            text-align: center; 
            border-radius: 10px; 
            padding: 16px; 
            position: fixed; 
            z-index: 3000; 
            left: 50%; 
            bottom: 30px; 
            transform: translateX(-50%); 
            font-weight: bold; 
            font-family: 'Orbitron';
            box-shadow: 0 5px 25px rgba(0,0,0,0.5);
            font-size: 14px;
        }
        #toast.show { visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }
        @keyframes fadein { from {bottom: 0; opacity: 0;} to {bottom: 30px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 30px; opacity: 1;} to {bottom: 0; opacity: 0;} }
        @keyframes fa-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .spin { animation: fa-spin 0.8s ease-in-out; }
    </style>
</head>
<body>

<div class="bg-grid-container">
    <div class="bg-grid"></div>
</div>

<div class="overlay" id="overlay"></div>
<div class="sidebar" id="sidebar">
    <div class="sidebar-header">SUNUCU SEÇİMİ</div>
    {% for srv in servers_list %}
    <a href="/?sid={{ srv.id }}" class="server-item {% if srv.id == current_server.id %}active{% endif %}">
        <i class="fas fa-server" style="margin-right: 10px;"></i>
        {{ srv.name }}
    </a>
    {% endfor %}
</div>
<nav class="navbar">
    <div class="logo-box">
        <div class="menu-btn" onclick="toggleMenu()">
            <i class="fas fa-bars"></i>
        </div>
        <img src="{{ url_for('static', filename=current_server.logo) }}" alt="Logo" class="nav-logo" onerror="this.style.display='none'">
        <span class="logo-text">{{ current_server.short_name }}</span>
        <span class="current-tag">{{ current_server.name }}</span>
    </div>
    <div class="social-box">
        <a href="https://discord.gg/a51" target="_blank" class="discord-link">discord.gg/a51</a>
    </div>
</nav>
<div class="container">
    <div class="stats-grid">
        <div class="card" onclick="copyAndOpen('{{ waze_id }}', 'Waze')">
            <span class="label-small">SUNUCU SAHİBİ</span>
            <img src="{{ url_for('static', filename='waze.png') }}" class="admin-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png'">
            <span class="admin-name">Waze</span>
            <span style="font-size: 9px; color: #555;">ID KOPYALAMAK İÇİN TIKLA</span>
        </div>

        <div class="card">
            <span class="label-small">İSTATİSTİK</span>
            <div style="height: 100px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                 <div class="player-val">{{ count }}</div>
            </div>
            <span class="admin-name" style="font-size: 24px;">AKTİF OYUNCU</span>
            <span style="font-size: 9px; color: #555;">{{ current_server.name }}</span>
        </div>

        <div class="card" onclick="copyAndOpen('{{ lilknife_id }}', 'Lilknife')">
            <span class="label-small">SUNUCU SAHİBİ</span>
            <img src="{{ url_for('static', filename='lilknife.png') }}" class="admin-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png'">
            <span class="admin-name">Lilknife</span>
            <span style="font-size: 9px; color: #555;">ID KOPYALAMAK İÇİN TIKLA</span>
        </div>
    </div>
    
    <div class="search-area">
        <input type="text" id="search" class="search-input" placeholder="Oyuncu ara..." onkeyup="filterTable()">
        <button class="refresh-btn" onclick="refreshPage(this)">
            <i class="fas fa-sync-alt"></i>
        </button>
    </div>
    <div class="table-wrap">
        <table id="playerTable">
            <thead>
                <tr>
                    <th>DURUM</th>
                    <th>ID</th>
                    <th>OYUNCU ADI</th>
                    <th>STEAM HEX</th>
                    <th>DISCORD ID</th>
                </tr>
            </thead>
            <tbody>
                {% for player in players %}
                <tr>
                    <td><span style="height:8px; width:8px; background:#00ff88; border-radius:50%; display:inline-block; box-shadow:0 0 8px #00ff88;"></span></td>
                    <td>#{{ player.id }}</td>
                    <td><strong>{{ player.name }}</strong></td>
                    <td style="color: #5cc2ff; font-family: monospace;">{{ player.steam }}</td>
                    <td style="color: #a5b4fc; font-family: monospace;">{{ player.discord }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
<div id="toast">ID Kopyalandı!</div>
<script>
function toggleMenu() {
    document.getElementById('sidebar').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}
document.getElementById('overlay').onclick = toggleMenu;
function refreshPage(btn) {
    btn.querySelector('i').classList.add('spin');
    setTimeout(() => { window.location.reload(); }, 300);
}
function copyAndOpen(id, name) {
    const el = document.createElement('textarea');
    el.value = id;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    const toast = document.getElementById("toast");
    toast.innerText = name + " ID Kopyalandı!";
    toast.className = "show";
    setTimeout(function(){ toast.className = "hide"; }, 3000);
    window.location.href = "discord://"; 
}
function filterTable() {
    let input = document.getElementById("search");
    let filter = input.value.toLowerCase();
    let tr = document.getElementById("playerTable").getElementsByTagName("tr");
    for (let i = 1; i < tr.length; i++) {
        tr[i].style.display = tr[i].textContent.toLowerCase().includes(filter) ? "" : "none";
    }
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    user_agent = request.headers.get('User-Agent', '').lower()
    if "cron-job.org" in user_agent or "uptime" in user_agent:
        return "ok", 200 

    current_sid = request.args.get('sid', 'z5gxl9')
    current_server = next((s for s in SERVERS if s['id'] == current_sid), SERVERS[0])
    try:
        url = f"https://servers-frontend.fivem.net/api/servers/single/{current_sid}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        players_list = []
        if response.status_code == 200:
            data = response.json().get("Data", {})
            players_raw = data.get("players") or []
            players_raw = sorted(players_raw, key=lambda x: x.get("id", 0))
            for p in players_raw:
                steam, discord = "Yok", "Bağlı Değil"
                for identifier in p.get("identifiers", []):
                    if "steam:" in identifier: steam = identifier.split(":")[1]
                    elif "discord:" in identifier: discord = identifier.split(":")[1]
                players_list.append({"id": p.get("id"), "name": p.get("name"), "steam": steam, "discord": discord})
        return render_template_string(HTML_TEMPLATE, players=players_list, count=len(players_list), waze_id=WAZE_ID, lilknife_id=LILKNIFE_ID, servers_list=SERVERS, current_server=current_server)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, players=[], count=0, waze_id=WAZE_ID, lilknife_id=LILKNIFE_ID, servers_list=SERVERS, current_server=current_server)

@app.route("/ping")
def ping():
    return "ok", 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
