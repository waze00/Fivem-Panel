from flask import Flask, render_template_string
import requests

# Flask uygulamasını başlatıyoruz
app = Flask(__name__)

# BURASI ÖNEMLİ: Kendi sunucu kodunu buraya yaz
SERVER_ID = "z5gxl9" 

# Görünüm (Arayüz) Ayarları
HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>MDRP FiveM Oyuncu Paneli</title>
    <style>
        body {
            margin: 0;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .navbar {
            width: 100%;
            background: rgba(0,0,0,0.8);
            padding: 15px 0;
            text-align: center;
            border-bottom: 2px solid #00ffcc;
            margin-bottom: 30px;
        }
        .logo { font-size: 24px; font-weight: bold; color: #00ffcc; letter-spacing: 2px; }
        .container { width: 90%; max-width: 1000px; }
        .stats-card {
            background: rgba(0,0,0,0.5);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
            border: 1px solid #333;
        }
        .count { font-size: 28px; color: #00ff88; font-weight: bold; }
        input#search {
            width: 100%;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 8px;
            border: 2px solid #00ffcc;
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 16px;
            outline: none;
            box-sizing: border-box;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(0,0,0,0.6);
            border-radius: 10px;
            overflow: hidden;
        }
        th { background: #111; color: #00ffcc; padding: 15px; }
        td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        tr:hover { background: rgba(0,255,204,0.1); }
        .steam { color: #1b9fff; font-size: 13px; font-weight: bold; }
        .discord { color: #7289da; font-size: 13px; font-weight: bold; }
        .refresh-btn {
            display: inline-block;
            margin-top: 10px;
            padding: 8px 20px;
            background: #00ffcc;
            color: black;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="navbar">
    <div class="logo">MDRP FIVEM PANEL</div>
</div>

<div class="container">
    <div class="stats-card">
        <div class="count">Aktif Oyuncu: {{ count }}</div>
        <a href="/" class="refresh-btn">Listeyi Yenile</a>
    </div>

    <input type="text" id="search" placeholder="ID, İsim, Steam Hex veya Discord ID ile ara..." onkeyup="filterTable()">

    <table id="playerTable">
        <thead>
            <tr>
                <th>ID</th>
                <th>Oyuncu Adı</th>
                <th>Steam Hex</th>
                <th>Discord ID</th>
            </tr>
        </thead>
        <tbody>
            {% for player in players %}
            <tr>
                <td>{{ player.id }}</td>
                <td><strong>{{ player.name }}</strong></td>
                <td class="steam">{{ player.steam }}</td>
                <td class="discord">{{ player.discord }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<script>
function filterTable() {
    let input = document.getElementById("search");
    let filter = input.value.toLowerCase();
    let table = document.getElementById("playerTable");
    let tr = table.getElementsByTagName("tr");

    // Tablo başlığı hariç (i=1) tüm satırları dön
    for (let i = 1; i < tr.length; i++) {
        let rowContent = tr[i].textContent.toLowerCase();
        // Eğer satırın herhangi bir yerinde aranan kelime geçiyorsa göster, geçmiyorsa gizle
        if (rowContent.includes(filter)) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"<h1>FiveM API Hatası!</h1><p>Kod: {response.status_code}. Sunucu şu an yanıt vermiyor olabilir.</p>"

        data = response.json()
        server_data = data.get("Data", {})
        players_raw = server_data.get("players") or server_data.get("clients") or []

        players_list = []
        for p in players_raw:
            steam = "Bulunamadı"
            discord = "Bağlı Değil"
            
            # Identifiers içinden Steam ve Discord'u ayıklama
            identifiers = p.get("identifiers", [])
            for identifier in identifiers:
                if identifier.startswith("steam:"):
                    steam = identifier.replace("steam:", "")
                elif identifier.startswith("discord:"):
                    discord = identifier.replace("discord:", "")

            players_list.append({
                "id": p.get("id", "??"),
                "name": p.get("name", "Bilinmiyor"),
                "steam": steam,
                "discord": discord
            })

        return render_template_string(HTML, players=players_list, count=len(players_list))

    except Exception as e:
        return f"<h1>Bir Hata Oluştu</h1><p>{str(e)}</p>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)