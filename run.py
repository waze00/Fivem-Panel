import os
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# Tasarımın ve Tablonun Olduğu HTML Şablonu
HTML_SABLON = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>MDPVP Canlı Oyuncu Paneli</title>
    <style>
        body {
            margin: 0;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            font-family: 'Segoe UI', sans-serif;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .navbar {
            width: 100%;
            background: rgba(0,0,0,0.8);
            padding: 15px 40px;
            border-bottom: 2px solid #ff4444;
            margin-bottom: 30px;
            display: flex;
            box-sizing: border-box;
        }
        .logo { 
            font-size: 36px; 
            font-weight: 900; 
            color: #ff4444; 
            letter-spacing: 4px;
            margin: 0 auto;
        }
        .container { width: 95%; max-width: 1100px; }
        .stats-card {
            background: rgba(0,0,0,0.5);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .stats-side-text { font-size: 20px; font-weight: bold; width: 150px; }
        .count { font-size: 28px; color: #00ff88; font-weight: bold; flex-grow: 1; text-align: center; }
        input#search {
            width: 100%; padding: 15px; margin-bottom: 20px;
            border-radius: 8px; border: 2px solid #ff4444;
            background: rgba(0,0,0,0.3); color: white; outline: none; box-sizing: border-box;
            font-size: 16px;
        }
        table { width: 100%; border-collapse: collapse; background: rgba(0,0,0,0.6); border-radius: 10px; overflow: hidden; }
        th { background: #111; color: #ff4444; padding: 15px; text-transform: uppercase; }
        td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        tr:hover { background: rgba(255, 68, 68, 0.1); }
        .steam { color: #1b9fff; font-size: 12px; font-family: monospace; }
        .discord-id { color: #7289da; font-size: 12px; font-family: monospace; }
        .refresh-btn {
            display: block; margin: 10px auto 20px auto; padding: 10px 25px;
            background: #ff4444; color: white; text-decoration: none;
            border-radius: 5px; font-weight: bold; width: fit-content;
            transition: 0.3s;
        }
        .refresh-btn:hover { background: #cc0000; transform: scale(1.05); }
    </style>
</head>
<body>

<div class="navbar"><div class="logo">MDPVP</div></div>

<div class="container">
    <div class="stats-card">
        <div class="stats-side-text" style="text-align: left;">Waze</div>
        <div class="count">Aktif Oyuncu: {{ count }}</div>
        <div class="stats-side-text" style="text-align: right;">Lilknife</div>
    </div>
    
    <div style="text-align: center;"><a href="/" class="refresh-btn">🔄 Verileri Güncelle</a></div>

    <input type="text" id="search" placeholder="İsim, ID veya Hex kodu ile oyuncu ara...">
    
    <table id="playerTable">
        <thead>
            <tr>
                <th>Sunucu ID</th>
                <th>Oyuncu Adı</th>
                <th>Steam Hex</th>
                <th>Discord ID</th>
            </tr>
        </thead>
        <tbody>
            {% for player in players %}
            <tr>
                <td><strong>{{ player.id }}</strong></td>
                <td>{{ player.name }}</td>
                <td class="steam">{{ player.identifiers | select('darkblue', 'steam:') | first | default('Yok') }}</td>
                <td class="discord-id">{{ player.identifiers | select('darkblue', 'discord:') | first | default('Bağlı Değil') }}</td>
            </tr>
            {% endfor %}
            {% if not players %}
            <tr>
                <td colspan="4" style="padding: 50px; color: #aaa;">Şu an sunucuda kimse yok veya sunucuya bağlanılamıyor.</td>
            </tr>
            {% endif %}
        </tbody>
    </table>
</div>

<script>
document.getElementById("search").addEventListener("keyup", function() {
    let filter = this.value.toLowerCase();
    let rows = document.querySelectorAll("#playerTable tbody tr");
    rows.forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(filter) ? "" : "none";
    });
});
</script>

</body>
</html>
"""

@app.route('/')
def home():
    # BURAYI DÜZENLE: Kendi sunucu IP ve Portunu yaz (Örn: http://1.2.3.4:30120)
    SUNUCU_IP = "IP_ADRESI" 
    SUNUCU_PORT = "30120"
    API_URL = f"http://{SUNUCU_IP}:{SUNUCU_PORT}/players.json"

    try:
        # Sunucudan gerçek oyuncu listesini çekiyoruz
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            players_data = response.json()
        else:
            players_data = []
    except Exception as e:
        print(f"Hata: {e}")
        players_data = []

    return render_template_string(HTML_SABLON, count=len(players_data), players=players_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
