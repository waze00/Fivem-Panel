HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>MDPVP Oyuncu Paneli</title>
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
            padding: 15px 40px;
            border-bottom: 2px solid #ff4444;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-sizing: border-box;
        }
        .logo { 
            font-size: 36px; 
            font-weight: 900; 
            color: #ff4444; 
            letter-spacing: 4px;
        }
        .container { width: 90%; max-width: 1000px; }
        
        /* GÜNCELLENEN İSTATİSTİK KARTI */
        .stats-card {
            background: rgba(0,0,0,0.5);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 1px solid #333;
            display: flex;
            justify-content: space-between; /* Sol, Orta, Sağ boşlukları */
            align-items: center;
        }
        .stats-side-text {
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            width: 150px; /* Hizalamanın bozulmaması için sabit genişlik */
        }
        .text-left { text-align: left; }
        .text-right { text-align: right; }
        
        .count { 
            font-size: 28px; 
            color: #00ff88; 
            font-weight: bold; 
            flex-grow: 1; 
            text-align: center; 
        }
        /* --------------------------- */

        input#search {
            width: 100%;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 8px;
            border: 2px solid #ff4444;
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
        th { background: #111; color: #ff4444; padding: 15px; }
        td { padding: 12px; text-align: center; border-bottom: 1px solid #222; }
        tr:hover { background: rgba(255,68,68,0.1); }
        .steam { color: #1b9fff; font-size: 13px; font-weight: bold; }
        .discord-id { color: #7289da; font-size: 13px; font-weight: bold; }
        .refresh-btn {
            display: block;
            margin: 10px auto 0 auto;
            width: fit-content;
            padding: 8px 20px;
            background: #ff4444;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="navbar">
    <div class="logo" style="margin: 0 auto;">MDPVP</div> </div>

<div class="container">
    <div class="stats-card">
        <div class="stats-side-text text-left">Waze</div>
        <div class="count">Aktif Oyuncu: {{ count }}</div>
        <div class="stats-side-text text-right">Lilknife</div>
    </div>
    
    <div style="text-align: center; margin-bottom: 20px;">
        <a href="/" class="refresh-btn">Listeyi Yenile</a>
    </div>

    <input type="text" id="search" placeholder="ID, İsim, Steam Hex veya Discord ID ile ara...">
    
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
function filterTable() {
    let input = document.getElementById("search");
    let filter = input.value.toLowerCase();
    let table = document.getElementById("playerTable");
    let tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        let rowContent = tr[i].textContent.toLowerCase();
        if (rowContent.includes(filter)) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}
document.getElementById("search").addEventListener("keyup", filterTable);
</script>

</body>
</html>
"""
