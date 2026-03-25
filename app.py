from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Oyları ve isimleri tutan liste
db = {
    "toplam": 0,
    "isimler": []
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Efe 💗 Damla - Barışma Kampanyası</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background: #ffe6f2; padding: 20px; color: #333; }
        .card { background: white; padding: 30px; border-radius: 20px; display: inline-block; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 90%; }
        h1 { color: #d63384; margin-bottom: 10px; font-size: 28px; }
        p { margin-top: 5px; color: #666; font-size: 16px; }
        input { padding: 12px; width: 80%; border: 2px solid #ffb3d9; border-radius: 10px; margin-bottom: 15px; outline: none; transition: 0.3s; }
        input:focus { border-color: #ff4d94; box-shadow: 0 0 10px rgba(255, 77, 148, 0.3); }
        button { background: #ff4d94; border: none; color: white; padding: 15px 40px; font-size: 18px; border-radius: 10px; cursor: pointer; width: 100%; transition: 0.3s; }
        button:disabled { background: #cccccc; cursor: not-allowed; }
        #counter { font-size: 26px; font-weight: bold; margin: 20px 0; color: #ff4d94; }
        .liste { text-align: left; margin-top: 20px; font-size: 14px; color: #666; border-top: 1px solid #eee; padding-top: 10px; }
        
        /* Telegram Butonu Stili */
        .tg-link { 
            margin-top: 25px; 
            padding-top: 15px; 
            border-top: 2px solid #ffb3d9; 
        }
        .tg-link a { 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            gap: 10px; 
            color: #d63384; 
            text-decoration: none; 
            font-size: 16px; 
            font-weight: bold; 
            background: rgba(255, 77, 148, 0.1); 
            padding: 10px 15px; 
            border-radius: 15px; 
            transition: 0.3s; 
        }
        .tg-link a:hover { 
            background: rgba(255, 77, 148, 0.2); 
            box-shadow: 0 4px 10px rgba(214, 51, 132, 0.1); 
        }
        .tg-link a img { width: 20px; height: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Efe 💗 Damla</h1>
        <p>Aşk kazansın, barışmaları için destek ol!</p>
        
        <div id="form-alani">
            <input type="text" id="isim" placeholder="Senin Adın Ne?" maxlength="30">
            <button id="btn" onclick="oyVer()">EVET, BARIŞSINLAR! ❤️</button>
        </div>

        <div id="counter">Toplanan Destek: {{ veri.toplam }}</div>
        
        <div class="liste">
            <strong>Destek Verenler:</strong>
            <div id="isim-listesi">{{ ", ".join(veri.isimler) }}</div>
        </div>

        <div class="tg-link">
            <a href="https://t.me/hwsret" target="_blank">
                <span>💬 Mesaj Gönder: t.me/hwsret</span>
            </a>
        </div>
    </div>

    <script>
        // Sayfa açıldığında daha önce oy vermiş mi kontrol et
        if(localStorage.getItem('oyVerdi')) {
            kilitle();
        }

        function kilitle() {
            document.getElementById('isim').style.display = 'none';
            document.getElementById('btn').disabled = true;
            document.getElementById('btn').innerText = 'Desteğin İletildi ❤️';
        }

        function oyVer() {
            let ad = document.getElementById('isim').value.trim();
            if(ad.length < 2) { 
                alert("Lütfen geçerli bir isim yaz!"); 
                return; 
            }

            fetch('/oy', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({isim: ad})
            })
            .then(res => res.json())
            .then(data => {
                localStorage.setItem('oyVerdi', 'true');
                kilitle();
                guncelle(data);
            });
        }
        
        function guncelle(data) {
            document.getElementById('counter').innerText = "Toplanan Destek: " + data.toplam;
            document.getElementById('isim-listesi').innerText = data.isimler.join(", ");
        }

        // Her 3 saniyede bir oyları canlı güncelle
        setInterval(() => {
            fetch('/durum').then(res => res.json()).then(data => guncelle(data));
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, veri=db)

@app.route('/oy', methods=['POST'])
def oy():
    isim = request.json.get('isim')
    if isim and isim not in db["isimler"]: # Aynı isimle üst üste basılmasın
        db["toplam"] += 1
        db["isimler"].append(isim)
    return jsonify(db)

@app.route('/durum')
def durum():
    return jsonify(db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
