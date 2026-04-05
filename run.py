import os
import requests
import mysql.connector
import threading
from flask import Flask, render_template_string, url_for, request

app = Flask(__name__)

# Takip etmek istediğin sunucuların ID'lerini buraya ekle
SUNUCU_IDLERI = ["z5gxl9", "z5rgx4", "zrqlap", "epx97a", "zem7ky" ]

# MySQL Bilgileri (Aiven'dan aldığın şifreyi tırnak içine yaz)
db_config = {
    'host': 'fpanelwaze-mustafaefe4998-1339.g.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_y-_auvMaafLqJhxCaoG', 
    'database': 'defaultdb',
    'port': 21023
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Tabloları oluşturma fonksiyonu
def init_db():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS site_logs (id INT AUTO_INCREMENT PRIMARY KEY, ip VARCHAR(45), zaman TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS player_history (id INT AUTO_INCREMENT PRIMARY KEY, srv_id VARCHAR(50), p_name VARCHAR(255), p_steam VARCHAR(100), p_discord VARCHAR(100), zaman TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

# --- SUNUCU TANIMLAMALARI ---
SERVERS = [
    {"id": "z5gxl9", "name": "MDPVP", "short_name": "MDPVP", "logo": "mdpvp.gif", "primary_color": "#ff1d1d", "accent_color": "#ffffff"},
    {"id": "z5rgx4", "name": "WELLGUN 8.SEZON", "short_name": "WELLGUN", "logo": "wellgun.gif", "primary_color": "#ffffff", "accent_color": "#ffffff"},
    {"id": "zrqlap", "name": "LETRA X", "short_name": "LETRA", "logo": "letra.gif", "primary_color": "#1b5e8b", "accent_color": "#ecf0f1"},
    {"id": "epx97a", "name": "DADDY 1.0", "short_name": "DADDY", "logo": "daddy.png", "primary_color": "#cc2e2e", "accent_color": "#ffffff"},
    {"id": "zem7ky", "name": "GUID PVP 3.0", "short_name": "GUID", "logo": "guid.gif", "primary_color": "#beaf1f", "accent_color": "#ffffff"},
]

WAZE_ID = "827593836229296188"
LILKNIFE_ID = "821434006843031624"

# --- SENİN TASARIMIN (TAMAMI) ---
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
            --primary-grid: {{ current_server.primary_color }}26;
            --primary-glow: {{ current_server.primary_color }}1A;
            --accent: {{ current_server.accent_color }};
            --bg: #030305;
            --card: rgba(10, 10, 14, 0.96);
            --discord-blue: #5865F2;
        }
        
        body { margin: 0; background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; overflow-x: hidden; min-height: 100vh; }
        
        body::before {
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: radial-gradient(circle at 50% 50%, var(--primary-glow) 0%, transparent 70%),
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);
            z-index: -2;
        }
        .bg-grid-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; perspective: 350px; z-index: -1; overflow: hidden; opacity: 0.8; }
        .bg-grid { position: absolute; width: 200%; height: 200%; top: -50%; left: -50%; background-image: linear-gradient(var(--primary-grid) 1px, transparent 1px), linear-gradient(90deg, var(--primary-grid) 1px, transparent 1px); background-size: 60px 60px; transform: rotateX(45deg); animation: grid-flow 20s linear infinite; -webkit-mask-image: radial-gradient(circle, rgba(0,0,0,1) 10%, rgba(0,0,0,0) 70%); }
        @keyframes grid-flow { from { transform: rotateX(45deg) translateY(0); } to { transform: rotateX(45deg) translateY(60px); } }
        
        .navbar { 
            padding: 0 3%; background: rgba(0, 0, 0, 0.98); 
            border-bottom: 2px solid var(--primary); display: flex; 
            justify-content: space-between; align-items: center; 
            position: sticky; top: 0; z-index: 1000; height: 80px;
            backdrop-filter: blur(10px);
        }

        .logo-box { display: flex; align-items: center; width: 300px; flex-shrink: 0; }
        .social-box { width: 300px; text-align: right; flex-shrink: 0; }

        .nav-logo { height: 50px; filter: drop-shadow(0 0 12px var(--primary)); }
        .logo-text { font-family: 'Audiowide'; font-size: 24px; color: #fff; margin-left: 12px; }
        
        .current-tag { 
            font-family: 'Orbitron'; font-size: 10px; color: var(--accent); 
            margin-left: 10px; border: 1px solid var(--primary-grid); 
            padding: 2px 6px; border-radius: 4px; opacity: 0.8;
            background: rgba(255,255,255,0.02);
        }

        .nav-server-switcher { 
            flex-grow: 1; 
            display: flex; 
            justify-content: center; 
            gap: 12px; 
            overflow-x: auto; 
            scrollbar-width: none; 
            padding: 0 10px; 
        }
        .nav-server-switcher::-webkit-scrollbar { display: none; }

        .nav-srv-tab {
            padding: 8px 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
            border-radius: 25px; color: #888; text-decoration: none; font-family: 'Orbitron'; font-size: 11px;
            font-weight: 800; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; gap: 8px;
            white-space: nowrap;
        }
        .nav-srv-tab-icon { width: 16px; height: 16px; border-radius: 50%; object-fit: cover; }
        
        .nav-srv-tab:hover { background: rgba(255,255,255,0.1); color: #fff; border-color: var(--primary); transform: translateY(-2px); }
        .nav-srv-tab.active { 
            background: var(--primary); color: #000; 
            border-color: var(--primary); box-shadow: 0 0 15px var(--primary-grid); 
        }

        .discord-link { 
            font-family: 'Orbitron'; color: #fff; text-decoration: none; 
            font-size: 13px; font-weight: 900; transition: 0.3s; 
            display: flex; align-items: center; justify-content: flex-end; gap: 8px;
        }
        .discord-link:hover { color: var(--discord-blue); text-shadow: 0 0 15px var(--discord-blue); transform: scale(1.05); }
        
        .container { width: 92%; max-width: 1300px; margin: 40px auto; position: relative; z-index: 1; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; margin-bottom: 40px; }
        .card { 
            background: var(--card); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; 
            padding: 30px; text-align: center; transition: 0.4s; cursor: pointer; position: relative; overflow: hidden;
        }
        .card::after {
            content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at center, var(--primary-glow) 0%, transparent 80%);
            opacity: 0; transition: 0.4s;
        }
        .card:hover { border-color: var(--primary); transform: translateY(-8px); box-shadow: 0 15px 45px -10px var(--primary-grid); }
        .card:hover::after { opacity: 1; }

        .admin-name { font-family: 'Orbitron'; font-size: 32px; font-weight: 900; color: #fff; margin-bottom: 10px; display: block; position: relative; z-index: 2; }
        .admin-img { width: 100px; height: 100px; border-radius: 50%; border: 3px solid rgba(255,255,255,0.05); margin-bottom: 15px; position: relative; z-index: 2; }
        .player-val { font-family: 'Orbitron'; font-size: 60px; color: var(--accent); text-shadow: 0 0 30px var(--primary); font-weight: 900; position: relative; z-index: 2; }
        .label-small { color: #777; font-size: 11px; letter-spacing: 3px; font-weight: 800; margin-bottom: 8px; display: block; position: relative; z-index: 2; }
        
        .card-server-name { font-family: 'Orbitron'; font-size: 10px; color: #555; display: block; margin-top: 12px; letter-spacing: 2px; text-transform: uppercase; position: relative; z-index: 2; }

        .search-area { display: flex; gap: 12px; margin-bottom: 25px; }
        .search-input { flex-grow: 1; padding: 16px 20px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; color: #fff; outline: none; transition: 0.3s; }
        .search-input:focus { border-color: var(--primary); box-shadow: 0 0 15px var(--primary-grid); }
        
        .refresh-btn { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); color: #fff; padding: 16px 20px; border-radius: 12px; cursor: pointer; transition: 0.3s; }
        .refresh-btn:hover { background: var(--primary); box-shadow: 0 0 15px var(--primary); transform: rotate(15deg); }
        
        .table-wrap { background: var(--card); border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
        table { width: 100%; border-collapse: collapse; }
        th { background: rgba(255,255,255,0.02); padding: 20px; text-align: left; color: var(--primary); font-family: 'Orbitron'; font-size: 11px; border-bottom: 2px solid var(--primary-grid); }
        td { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.02); font-size: 14px; transition: 0.2s; }
        tr:hover td { background: rgba(255,255,255,0.03); color: var(--accent); }
        
        #toast { 
            visibility: hidden; min-width: 250px; 
            background-color: var(--primary); 
            color: #000; 
            text-align: center; border-radius: 10px; padding: 16px; 
            position: fixed; z-index: 3000; left: 50%; bottom: 30px; 
            transform: translateX(-50%); font-family: 'Orbitron'; font-weight: bold; 
        }
        
        #toast.show { visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }
        @keyframes fadein { from {bottom: 0; opacity: 0;} to {bottom: 30px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 30px; opacity: 1;} to {bottom: 0; opacity: 0;} }
        .spin { animation: fa-spin 0.8s ease-in-out; }
        @keyframes fa-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div class="bg-grid-container">
    <div class="bg-grid"></div>
</div>

<nav class="navbar">
    <div class="logo-box">
        <img src="{{ url_for('static', filename=current_server.logo) }}" alt="Logo" class="nav-logo" onerror="this.style.display='none'">
        <span class="logo-text">{{ current_server.short_name }}</span>
        <span class="current-tag">{{ current_server.short_name }}</span>
    </div>

    <div class="nav-server-switcher">
        {% for srv in servers_list %}
        <a href="/?sid={{ srv.id }}" class="nav-srv-tab {% if srv.id == current_server.id %}active{% endif %}">
            <img src="{{ url_for('static', filename=srv.logo) }}" class="nav-srv-tab-icon" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png';">
            {{ srv.name }}
        </a>
        {% endfor %}
    </div>

    <div class="social-box">
        <a href="https://discord.gg/a51" target="_blank" class="discord-link">
            <i class="fab fa-discord"></i> discord.gg/a51
        </a>
    </div>
</nav>

<div class="container">
    <div class="stats-grid">
        <div class="card" onclick="copyAndOpen('{{ waze_id }}', 'Waze')">
            <img src="{{ url_for('static', filename='waze.png') }}" class="admin-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png'">
            <span class="admin-name">Waze</span>
            <span style="font-size: 8px; color: #555;">ID KOPYALAMAK İÇİN TIKLA</span>
        </div>

        <div class="card">
            <span class="label-small">İSTATİSTİK</span>
            <div style="height: 100px; display: flex; align-items: center; justify-content: center;">
                 <div class="player-val">{{ count }}</div>
            </div>
            <span class="admin-name" style="font-size: 26px;">AKTİF OYUNCU</span>
            <span class="card-server-name">{{ current_server.short_name }}</span>
        </div>

        <div class="card" onclick="copyAndOpen('{{ lilknife_id }}', 'Lilknife')">
            <img src="{{ url_for('static', filename='lilknife.png') }}" class="admin-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png'">
            <span class="admin-name">Lilknife</span>
            <span style="font-size: 8px; color: #555;">ID KOPYALAMAK İÇİN TIKLA</span>
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
                    <td><span style="height:10px; width:10px; background:#00ff88; border-radius:50%; display:inline-block; box-shadow:0 0 10px #00ff88;"></span></td>
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
    setTimeout(function(){ toast.className = ""; }, 3000);
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

# --- CRON JOB İÇİN ÖZEL PİNG YOLU ---
@app.route("/ping")
def ping():
    def background_task():
        # Her ping atıldığında tüm sunucuları değil, 
        # API'yi yormamak için sırayla veya kontrollü çekelim
        for srv in SERVERS:
            try:
                sid = srv['id']
                url = f"https://servers-frontend.fivem.net/api/servers/single/{sid}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json().get("Data", {})
                    players_raw = data.get("players") or []
                    
                    # Mevcut kayıt fonksiyonunu çağır
                    update_history_bg(sid, players_raw)
            except Exception as e:
                print(f"Cron hatası ({srv['name']}): {e}")

    # İşlemi arka planda başlat ki Cron Job hemen "200 OK" alabilsin
    threading.Thread(target=background_task).start()
    return "Veri toplama tetiklendi", 200

import threading # Dosyanın en üstüne bunu eklemeyi unutma!

def update_history_bg(srv_id, players_raw):
    # Veritabanı bilgilerini buraya gir
    db = pymysql.connect(host="...", user="...", password="...", database="...")
    try:
        with db.cursor() as cursor:
            for p in players_raw:
                p_name = p.get('name', 'Bilinmiyor')
                ids = p.get('identifiers', [])
                
                # Steam ve Discord ID'leri varsa al, yoksa "Yok" yaz
                p_steam = next((i for i in ids if "steam" in i), "Yok")
                p_discord = next((i for i in ids if "discord" in i), "Yok")

                sql = """
                    INSERT INTO player_history (srv_id, p_name, p_steam, p_discord) 
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        p_steam = VALUES(p_steam),
                        p_discord = VALUES(p_discord),
                        zaman = CURRENT_TIMESTAMP
                """
                cursor.execute(sql, (srv_id, p_name, p_steam, p_discord))
        db.commit()
    finally:
        db.close()
        
    except Exception as e:
        print(f"Hata: {e}")
        
@app.route("/")
def home():
    current_sid = request.args.get('sid', 'z5gxl9') # Varsayılan server
    current_server = next((s for s in SERVERS if s['id'] == current_sid), SERVERS[0])
    
    players_list = []
    count = 0
    
    try:
        # 1. Önce sadece FiveM API'den veriyi çekiyoruz (Hızlı işlem)
        url = f"https://servers-frontend.fivem.net/api/servers/single/{current_sid}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
        response = requests.get(url, headers=headers, timeout=5) 
        
        if response.status_code == 200:
            data = response.json().get("Data", {})
            players_raw = data.get("players") or []
            
            # Ekranda görünecek listeyi hızlıca hazırla
            for p in players_raw:
                steam, discord = "Yok", "Bağlı Değil"
                for identifier in p.get("identifiers", []):
                    if "steam:" in identifier: steam = identifier.split(":")[1]
                    elif "discord:" in identifier: discord = identifier.split(":")[1]
                players_list.append({"id": p.get("id"), "name": p.get("name"), "steam": steam, "discord": discord})
            
            count = len(players_list)
            if count == 0 and data.get("clients"):
                count = data.get("clients")

            count = len(players_list)
            
            # --- SIRALAMA BURAYA GELİYOR ---
            # ID'leri sayıya çevirerek (int) küçükten büyüğe sıralar
            players_list.sort(key=lambda x: int(x['id']))
            # ------------------------------

            if count == 0 and data.get("clients"):
                count = data.get("clients")

            # 2. KRİTİK NOKTA: Veritabanı işini arka plana at ve bekleme!
            # Bu satır sayesinde site veritabanını beklemeden açılır.
            threading.Thread(target=update_history_bg, args=(current_sid, players_raw)).start()

    except Exception as e:
        print(f"Ana sayfa hatası: {e}")

    # 3. Hemen sayfayı render et (Kullanıcı beklemesin)
    return render_template_string(HTML_TEMPLATE, players=players_list, count=count, waze_id=WAZE_ID, lilknife_id=LILKNIFE_ID, servers_list=SERVERS, current_server=current_server)

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
