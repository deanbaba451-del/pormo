import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
import threading

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBu2WXMCBnEwAlcTBvFe5m3qWws8Yu6L7xhKgZyiJPxilJSXzv1wB6z4zHaWfSuTVOHEftRNljNMpe3VVt7D5MZTNGRxDjWObbPVST4dqw2GtpM3kC3npiFQvKHIV3zJwG1OAWFeW5XqmXeOAcKxg73PrxPBqTZVwYfQdWWVKTQc1r7NF_NNmLM1xa4s559jQzXUU6gJlbgoPHwKsTpjTZvTEIQlcRGd1Cj77GzBxEAoVQX9dTxgc5OxmoUMM85XIm6y8JWPSlSn3p9Kz12bCQv-H-ThL9iZMYJzN1C9RE4wAJ3hvISmu8QeC5ogkUKa_Ek-hiuwltf5V5geLReKcUb3Q='

AUTHORIZED_USERS = [8256872080, 6534222591, 7727812432, 8343507331]
mode = "normal" 

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Aktif ve 7/24 Calisiyor"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    # Flask'ı debug modsuz ve thread güvenli şekilde çalıştırıyoruz
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

@client.on(events.NewMessage)
async def handler(event):
    global mode
    sender_id = event.sender_id
    text = event.raw_text.lower() if event.raw_text else ""

    if sender_id in AUTHORIZED_USERS:
        if text == "/aktifmedya":
            mode = "aktifmedya"
            await event.respond("🛡 **Medya Filtresi Aktif:** Sadece ses ve metin atılabilir.")
            return
        elif text in ["/durmedya", "/durchat"]:
            mode = "normal"
            await event.respond("✅ **Filtreler Kapatıldı:** Her şey serbest.")
            return
        elif text == "/aktifchat":
            mode = "aktifchat"
            await event.respond("🚫 **Chat Kilitlendi:** Tüm yeni mesajlar temizlenecek.")
            return

    if mode == "aktifmedya":
        is_text = event.text and not event.media
        is_voice = event.voice or event.audio
        if not (is_text or is_voice):
            try: await event.delete()
            except: pass

    elif mode == "aktifchat":
        if not (sender_id in AUTHORIZED_USERS and text == "/durchat"):
            try: await event.delete()
            except: pass

async def main():
    # Botu başlat
    await client.start()
    print("Bot başarıyla başlatıldı!")
    # Bağlantı kopana kadar beklet
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Flask'ı ayrı bir thread'de başlat
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Python 3.14+ uyumlu yeni başlatma yöntemi
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
