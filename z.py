import asyncio
import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"

# YENİ ALDIĞIN STRINGI BURAYA YAPIŞTIRDIM
SESSION_STRING = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="

# Komutları sadece sen (bu ID) verebilirsin
SUPER_ADMIN = 6534222591

# --- FLASK (Render'ın Kapanmaması İçin) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Nuke Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
nuke_active = False

@client.on(events.NewMessage(pattern=r'\.xon'))
async def start_nuke(event):
    global nuke_active
    if event.sender_id == SUPER_ADMIN:
        nuke_active = True
        await event.edit("online")

@client.on(events.NewMessage(pattern=r'\.xoff'))
async def stop_nuke(event):
    global nuke_active
    if event.sender_id == SUPER_ADMIN:
        nuke_active = False
        await event.edit("offline")

@client.on(events.NewMessage)
async def nuke_handler(event):
    global nuke_active
    # Nuke kapalıysa, mesajı atan bizsek veya komutsa silme
    if not nuke_active or event.sender_id == (await client.get_me()).id:
        return
    
    if event.text in ['.xon', '.xoff']:
        return

    try:
        await event.delete()
    except:
        pass

async def main():
    print("Bot başlatılıyor...")
    await client.start()
    me = await client.get_me()
    print(f"Giriş Başarılı: {me.first_name} (ID: {me.id})")
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Flask sunucusunu başlat
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Botu ana döngüde çalıştır
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
