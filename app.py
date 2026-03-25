from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Oyları tutan basit bir değişken (Sunucu açık kaldığı sürece tutulur)
data = {"evet": 0}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Efe & Damla</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; text-align: center; background: #ffe6f2; padding-top: 50px; }
        .card { background: white; padding: 20px; border-radius: 15px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h1 { color: #d63384; }
        button { background: #ff4d94; border: none; color: white; padding: 15px 30px; font-size: 18px; border-radius: 10px; cursor: pointer; }
        #counter { font-size: 24px; font-weight: bold; margin-top: 20px; color: #333; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Efe 💗 Damla</h1>
        <p>Sizce barışsınlar mı?</p>
        <button onclick="oyVer()">EVET!</button>
        <div id="counter">Canlı Destek: {{ evet_sayisi }}</div>
    </div>

    <script>
        function oyVer() {
            fetch('/oy', {method: 'POST'})
            .then(res => res.json())
            .then(data => {
                document.getElementById('counter').innerText = "Canlı Destek: " + data.evet;
            });
        }
        
        // Her 3 saniyede bir oyları güncelle (Canlı takip için)
        setInterval(() => {
            fetch('/durum')
            .then(res => res.json())
            .then(data => {
                document.getElementById('counter').innerText = "Canlı Destek: " + data.evet;
            });
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, evet_sayisi=data["evet"])

@app.route('/oy', methods=['POST'])
def oy():
    data["evet"] += 1
    return jsonify(data)

@app.route('/durum')
def durum():
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
