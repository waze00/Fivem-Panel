import os
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# Tasarımın bozulmaması için HTML değişkenini buraya sabitledik
HTML_SABLON = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>MDPVP Oyuncu Paneli</title>
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
        .container { width: 90%; max-width: 1000px; }
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
            width: 100%; padding: 12px; margin-bottom: 20px;
            border-radius: 8px; border: 2px solid #ff4444;
            background: rgba(0,0,0,0.3); color: white; outline: none; box-sizing: border-box;
        }
        table { width: 100%; border-collapse: collapse; background: rgba(0,0,0,0.6); border-radius: 10px; overflow: hidden; }
        th { background: #111; color: #ff4444; padding: 15px; }
        td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        .steam { color: #1b9fff; font-size: 13px; }
        .discord-id { color: #7289da; font-size: 13px; }
        .refresh-btn {
            display: block; margin: 10px auto; padding: 8px 20px;
            background: #ff4444; color: white; text-decoration: none;
            border-radius: 5px; font-weight: bold; width: fit-content;
        }
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
    
    <div style="text-align: center;"><a href="/" class="refresh-btn">Listeyi Yenile</a></div>

    <input type="text" id="search" placeholder="Ara...">
    
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
                <td class="discord-id">{{ player.discord }}</td>
            </tr>
            {% endfor %}
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
    # TEST VERİSİ (Burayı FiveM IP'n ile bağlayabilirsin)
    test_players = [
        {"id": 1, "name": "Waze", "steam": "steam:1100001", "discord": "123456789"},
        {"id": 2, "name": "Lilknife", "steam": "steam:1100002", "discord": "987654321"}
    ]
    return render_template_string(HTML_SABLON, count=len(test_players), players=test_players)

if __name__ == "__main__":
    # RENDER İÇİN EN ÖNEMLİ KISIM
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
