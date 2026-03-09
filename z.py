import os
import asyncio
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
import threading

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBu2WXMCBnEwAlcTBvFe5m3qWws8Yu6L7xhKgZyiJPxilJSXzv1wB6z4zHaWfSuTVOHEftRNljNMpe3VVt7D5MZTNGRxDjWObbPVST4dqw2GtpM3kC3npiFQvKHIV3zJwG1OAWFeW5XqmXeOAcKxg73PrxPBqTZVwYfQdWWVKTQc1r7NF_NNmLM1xa4s559jQzXUU6gJlbgoPHwKsTpjTZvTEIQlcRGd1Cj77GzBxEAoVQX9dTxgc5OxmoUMM85XIm6y8JWPSlSn3p9Kz12bCQv-H-ThL9iZMYJzN1C9RE4wAJ3hvISmu8QeC5ogkUKa_Ek-hiuwltf5V5geLReKcUb3Q='

AUTHORIZED_USERS = [8256872080, 6534222591, 7727812432, 8343507331]

# Grup bazlı durumları saklamak için sözlük (Key: Chat ID, Value: Mod)
group_modes = {}

# Kart ve Telefon Numarası tespiti için Regex (Düzenli İfade)
CARD_PATTERN = r'\b(?:\d[ -]*?){13,16}\b' # 13-16 haneli rakamlar
PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}' # Türkiye telefon formatı

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Aktif"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

@client.on(events.NewMessage)
async def handler(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    text = event.raw_text if event.raw_text else ""
    
    # Mevcut grubun modunu al (Yoksa 'normal' kabul et)
    current_mode = group_modes.get(chat_id, "normal")

    # 1. BOTLARI VE KENDİNİ KORU: Eğer mesaj bir bottan geliyorsa dokunma
    if event.sender and event.sender.bot:
        return

    # 2. ÖZEL FİLTRE: Komutlardan bağımsız Kart ve Telefon Numarası silme
    if re.search(CARD_PATTERN, text) or re.search(PHONE_PATTERN, text):
        try:
            await event.delete()
            return # Kart/Numara sildiyse diğer kontrollere bakmaya gerek yok
        except: pass

    # 3. KOMUT KONTROLÜ (Sadece Yetkililer)
    if sender_id in AUTHORIZED_USERS:
        cmd = text.lower()
        if cmd == "/aktifmedya":
            group_modes[chat_id] = "aktifmedya"
            await event.respond("🛡 **Medya Filtresi Bu Grup İçin Aktif:** Sadece ses ve metin.")
            return
        elif cmd in ["/durmedya", "/durchat"]:
            group_modes[chat_id] = "normal"
            await event.respond("✅ **Filtreler Bu Grup İçin Kapatıldı.**")
            return
        elif cmd == "/aktifchat":
            group_modes[chat_id] = "aktifchat"
            await event.respond("🚫 **Chat Bu Grup İçin Kilitlendi:** Her şey silinecek.")
            return

    # 4. GRUP BAZLI FİLTRELEME MANTIĞI
    if current_mode == "aktifmedya":
        is_text = event.text and not event.media
        is_voice = event.voice or event.audio
        if not (is_text or is_voice):
            try: await event.delete()
            except: pass

    elif current_mode == "aktifchat":
        # Yetkili /durchat yazmadıysa sil
        if not (sender_id in AUTHORIZED_USERS and text.lower() == "/durchat"):
            try: await event.delete()
            except: pass

async def main():
    await client.start()
    print("Bot gruplara özel modla çalışıyor...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
