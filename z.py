import os
import asyncio
import re
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask
import threading

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='

AUTHORIZED_USERS = [8256872080, 6534222591, 7727812432, 8343507331]

group_modes = {}

# Kart ve Telefon Numarası tespiti
CARD_PATTERN = r'\b(?:\d[ -]*?){13,16}\b'
PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home():
    return "Sistem Aktif"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

@client.on(events.NewMessage)
async def handler(event):
    chat_id = event.chat_id
    sender = await event.get_sender()
    
    # 1. BOT KORUMASI: Gönderen bir botsa ASLA işlem yapma
    if hasattr(sender, 'bot') and sender.bot:
        return
    
    # Kendi mesajlarını da pas geç (Userbot olduğu için kendi komutlarını silmesin)
    if event.is_reply and event.sender_id == (await client.get_me()).id:
        return

    text = event.raw_text if event.raw_text else ""
    current_mode = group_modes.get(chat_id, "normal")

    # 2. OTOMATİK SİLİCİ (Kart/Numara) - Moddan bağımsız çalışır
    if re.search(CARD_PATTERN, text) or re.search(PHONE_PATTERN, text):
        try:
            await event.delete()
            return 
        except: pass

    # 3. YETKİLİ KOMUTLARI
    if event.sender_id in AUTHORIZED_USERS:
        cmd = text.lower().strip()
        if cmd == "/aktifmedya":
            group_modes[chat_id] = "aktifmedya"
            await event.respond("🛡 **Medya Filtresi Aktif:** Sadece ses ve metin.")
            return
        elif cmd in ["/durmedya", "/durchat"]:
            group_modes[chat_id] = "normal"
            await event.respond("✅ **Filtreler Durduruldu.**")
            return
        elif cmd == "/aktifchat":
            group_modes[chat_id] = "aktifchat"
            await event.respond("🚫 **Chat Kilitlendi:** Tüm yeni mesajlar siliniyor.")
            return

    # 4. MODA GÖRE SİLME
    if current_mode == "aktifmedya":
        # Ses veya sadece metin değilse sil
        is_voice = event.voice or event.audio or event.video_note
        is_pure_text = event.text and not event.media
        
        if not (is_pure_text or is_voice):
            try: await event.delete()
            except: pass

    elif current_mode == "aktifchat":
        # Yetkili komutu değilse her şeyi sil
        if not (event.sender_id in AUTHORIZED_USERS and text.lower() == "/durchat"):
            try: await event.delete()
            except: pass

async def main():
    await client.start()
    print("Bot 7/24 Filtreleme Modunda...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
