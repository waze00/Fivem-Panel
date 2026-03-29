import os
import requests
from flask import Flask, render_template_string, url_for

app = Flask(__name__)

SERVER_ID = "z5gxl9" 

# --- YÖNETİCİ BİLGİLERİ ---
WAZE_ID = "827593836229296188"
LILKNIFE_ID = "821434006843031624"
# ---------------------------

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDPVP | Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Audiowide&family=Inter:wght@400;700;900&family=Orbitron:wght@800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #ff1d1d;
            --cyan: #00f2fe;
            --bg: #050507;
            --card: rgba(18, 18, 22, 0.95);
            --discord-blue: #5865F2;
        }

        body { margin: 0; background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        
        body::before {
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: radial-gradient(circle at 50% 50%, rgba(255, 29, 29, 0.05) 0%, transparent 50%),
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px), 
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 50px 50px, 50px 50px; z-index: -1;
        }

        .navbar { 
            padding: 10px 5%; 
            background: rgba(0, 0, 0, 0.9); 
            border-bottom: 2px solid var(--primary); 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        
        .logo-box { 
            display: flex; 
            align-items: center; 
            gap: 15px; /* Boşluk bir tık artırıldı */
        }
        
        .nav-logo {
            height: 65px; /* Logo boyutu büyütüldü */
            width: auto;
            filter: drop-shadow(0 0 10px rgba(255, 29, 29, 0.6));
            transition: transform 0.3s ease;
        }

        .logo-box:hover .nav-logo {
            transform: scale(1.05);
        }

        .logo-text { font-family: 'Audiowide'; font-size: 30px; letter-spacing: 2px; color: #fff; }

        .discord-link {
            font-family: 'Orbitron';
            color: #ffffff;
            text-decoration: none;
            font-size: 16px;
            font-weight: 800;
            transition: 0.3s ease;
            letter-spacing: 1px;
        }
        .discord-link:hover {
            color: var(--discord-blue);
            text-shadow: 0 0 10px rgba(88, 101, 242, 0.5);
        }

        .container { width: 90%; max-width: 1200px; margin: 50px auto; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-bottom: 40px; }

        .card {
            background: var(--card); border: 1px solid rgba(255,255,255,0.05);
            border-radius: 15px; padding: 40px 20px; text-align: center;
            transition: 0.3s ease; cursor: pointer; position: relative;
        }

        .card:hover { 
            border-color: var(--primary); 
            transform: translateY(-5px); 
            box-shadow: 0 0 30px rgba(255, 29, 29, 0.2); 
        }

        .admin-name { 
            font-family: 'Orbitron'; font-size: 35px; font-weight: 900; 
            background: linear-gradient(to bottom, #fff, #888);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 15px; display: block;
        }

        .admin-img {
            width: 120px; height: 120px; border-radius: 50%; border: 3px solid rgba(255,255,255,0.1);
            transition: 0.3s; margin-bottom: 15px;
        }

        .player-val { font-family: 'Orbitron'; font-size: 60px; color: var(--cyan); text-shadow: 0 0 20px rgba(0,242,254,0.4); }
        .label-small { color: #555; font-size: 11px; letter-spacing: 3px; font-weight: 800; margin-bottom: 10px; display: block; }

        .search-area { position: relative; display: flex; align-items: center; gap: 10px; margin-bottom: 25px; }

        .search-input {
            flex-grow: 1; padding: 18px; background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
            color: #fff; outline: none; transition: 0.3s;
        }
        .search-input:focus { border-color: var(--primary); background: rgba(255,255,255,0.08); }

        .refresh-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            padding: 15px 20px;
            border-radius: 12px;
            cursor: pointer;
            transition: 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .refresh-btn:hover { background: var(--primary); border-color: var(--primary); transform: rotate(15deg); }
        .refresh-btn:active { transform: scale(0.9); }
        
        .spin { animation: fa-spin 0.8s ease-in-out; }

        .table-wrap { background: var(--card); border-radius: 15px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
        table { width: 100%; border-collapse: collapse; }
        th { background: rgba(0,0,0,0.3); padding: 20px; text-align: left; color: var(--primary); font-family: 'Orbitron'; font-size: 11px; }
        td { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.02); }

        #toast {
            visibility: hidden; min-width: 250px; background-color: var(--primary);
            color: #fff; text-align: center; border-radius: 8px; padding: 16px;
            position: fixed; z-index: 100; left: 50%; bottom: 30px;
            transform: translateX(-50%); font-weight: bold;
        }
        #toast.show { visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }

        @keyframes fadein { from {bottom: 0; opacity: 0;} to {bottom: 30px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 30px; opacity: 1;} to {bottom: 0; opacity: 0;} }
    </style>
</head>
<body>

<nav class="navbar">
    <div class="logo-box">
        <img src="{{ url_for('static', filename='mdpvp.gif') }}" alt="Logo" class="nav-logo" onerror="this.style.display='none'">
        <span class="logo-text">MDPVP</span>
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
            <span style="font-size: 10px; color: #666;">ID KOPYALAMAK İÇİN TIKLA</span>
        </div>

        <div class="card" style="cursor: default; border-bottom: 3px solid var(--cyan);">
            <span class="label-small" style="color: var(--cyan)">AKTİF OYUNCU</span>
            <div class="player-val">{{ count }}</div>
        </div>

        <div class="card" onclick="copyAndOpen('{{ lilknife_id }}', 'Lilknife')">
            <span class="label-small">LEAD DEVELOPER</span>
            <img src="{{ url_for('static', filename='lilknife.png') }}" class="admin-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png'">
            <span class="admin-name">Lilknife</span>
            <span style="font-size: 10px; color: #666;">ID KOPYALAMAK İÇİN TIKLA</span>
        </div>
    </div>

    <div class="search-area">
        <input type="text" id="search" class="search-input" placeholder="Oyuncu ara..." onkeyup="filterTable()">
        <button class="refresh-btn" onclick="refreshPage(this)" title="Listeyi Yenile">
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
                    <td><span style="height:8px; width:8px; background:#00ff88; border-radius:50%; display:inline-block; box-shadow:0 0 10px #00ff88;"></span></td>
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
    const icon = btn.querySelector('i');
    icon.classList.add('spin');
    setTimeout(() => {
        window.location.reload();
    }, 300);
}

function copyAndOpen(id, name) {
    const el = document.createElement('textarea');
    el.value = id;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);

    const toast = document.getElementById("toast");
    toast.innerText = name + " ID Kopyalandı! Discord Açılıyor...";
    toast.className = "show";
    setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);

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
    try:
        url = f"https://servers-frontend.fivem.net/api/servers/single/{SERVER_ID}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        players_list = []
        if response.status_code == 200:
            data = response.json().get("Data", {})
            players_raw = data.get("players") or []
            for p in players_raw:
                steam, discord = "Yok", "Bağlı Değil"
                for identifier in p.get("identifiers", []):
                    if "steam:" in identifier: steam = identifier.split(":")[1]
                    elif "discord:" in identifier: discord = identifier.split(":")[1]
                players_list.append({"id": p.get("id"), "name": p.get("name"), "steam": steam, "discord": discord})
        
        return render_template_string(HTML_TEMPLATE, players=players_list, count=len(players_list), waze_id=WAZE_ID, lilknife_id=LILKNIFE_ID)
    except Exception as e:
        return f"Hata: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
