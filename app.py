import os
import json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Oyları kaydetmek için dosya adı
DATA_FILE = "oylar.json"

# Oyları dosyadan okuyan fonksiyon
def veri_oku():
    if not os.path.exists(DATA_FILE):
        return {"toplam": 0, "isimler": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"toplam": 0, "isimler": []}

# Oyları dosyaya yazan fonksiyon
def veri_yaz(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        pass

# Başlangıçta oyları yükle
db = veri_oku()

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Efe & Damla ❤️ Barışma Kampanyası</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background: #ffe6f2; padding: 20px; color: #333; }
        .card { background: white; padding: 30px; border-radius: 20px; display: inline-block; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 450px; width: 90%; }
        h1 { color: #d63384; margin-bottom: 5px; font-size: 26px; }
        p.main { margin-top: 0; color: #666; font-size: 15px; }
        input { padding: 12px; width: 85%; border: 2px solid #ffb3d9; border-radius: 10px; margin-bottom: 15px; outline: none; transition: 0.3s; font-size: 14px;}
        input:focus { border-color: #ff4d94; box-shadow: 0 0 10px rgba(255, 77, 148, 0.3); }
        button { background: #ff4d94; border: none; color: white; padding: 15px; font-size: 16px; border-radius: 10px; cursor: pointer; width: 100%; transition: 0.3s; font-weight: bold;}
        button:disabled { background: #cccccc; cursor: not-allowed; }
        #counter { font-size: 24px; font-weight: bold; margin: 20px 0; color: #ff4d94; }
        .liste { text-align: left; margin-top: 20px; font-size: 13px; color: #666; border-top: 1px solid #eee; padding-top: 10px; }
        
        /* Telegram Butonu */
        .tg-link { margin-top: 20px; font-size: 12px; }
        .tg-link a { color: #d63384; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 5px;}
        .tg-link a img { width: 15px; height: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Efe & Damla</h1>
        <p class="main">Aşk her şeyi yener. Barışmaları için sen de destek ol!</p>
        
        <div id="form-alani">
            <input type="text" id="isim" placeholder="Adınız Soyadınız" maxlength="30">
            <button id="btn" onclick="oyVer()">EVET, BARIŞSINLAR! ❤️</button>
        </div>

        <div id="counter">Toplanan Destek: <span id="toplam-sayi">{{ veri.toplam }}</span></div>
        
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
        if(localStorage.getItem('oyVerdi')) { kilitle(); }

        function kilitle() {
            document.getElementById('isim').style.display = 'none';
            document.getElementById('btn').disabled = true;
            document.getElementById('btn').innerText = 'Desteğin İletildi ❤️';
        }

        function oyVer() {
            let ad = document.getElementById('isim').value.trim();
            if(ad.length < 2) { alert("Lütfen adınızı yazın!"); return; }

            fetch('/oy', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({isim: ad})
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "hata") { alert(data.mesaj); return; }
                localStorage.setItem('oyVerdi', 'true');
                kilitle();
                guncelle(data);
            });
        }
        
        function guncelle(data) {
            document.getElementById('toplam-sayi').innerText = data.toplam;
            document.getElementById('isim-listesi').innerText = data.isimler.join(", ");
        }

        // Her 5 saniyede bir oyları canlı güncelle
        setInterval(() => {
            fetch('/durum').then(res => res.json()).then(data => guncelle(data));
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    global db
    db = veri_oku() # Her açılışta dosyadan oku (Render için daha güvenli)
    return render_template_string(HTML, veri=db)

@app.route('/oy', methods=['POST'])
def oy():
    isim = request.json.get('isim')
    if isim and isim not in db["isimler"]:
        db["toplam"] += 1
        db["isimler"].append(isim)
        veri_yaz(db) # Oyu hemen dosyaya kaydet
        return jsonify(db)
    return jsonify({"status": "hata", "mesaj": "Zaten oy verdiniz veya isim hatalı."})

@app.route('/durum')
def durum():
    return jsonify(veri_oku()) # Dosyadan en güncel halini oku

# Portu Render.com için otomatik ayarla
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
