import asyncio
import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION_STRING = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
MY_ID = 6534222591

# --- FLASK AYARI ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Active"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT MANTIĞI ---
client = TelegramClient(StringSession(SESSION_STRING.strip()), API_ID, API_HASH)
active_chats = set()

@client.on(events.NewMessage(pattern=r'\.b'))
async def start_nuke(event):
    if event.sender_id == MY_ID:
        active_chats.add(event.chat_id)
        await event.respond("online")

@client.on(events.NewMessage(pattern=r'\.i'))
async def stop_nuke(event):
    if event.sender_id == MY_ID:
        if event.chat_id in active_chats:
            active_chats.remove(event.chat_id)
        await event.respond("offline")

@client.on(events.NewMessage)
async def nuke_handler(event):
    if event.chat_id not in active_chats:
        return
    if event.sender_id == MY_ID or event.text in ['.b', '.i', 'online', 'offline']:
        return
    try:
        await event.delete()
    except:
        pass

# --- ANA ÇALIŞTIRICI (Python 3.14 Uyumlu) ---
async def start_all():
    # Flask'ı ayrı bir kanalda başlat
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Telegram'ı başlat
    await client.start()
    print("✅ BOT ŞU AN TELEGRAM'A BAĞLANDI!")
    
    # Bağlantıyı canlı tut
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Python 3.14 için en güvenli çalışma metodu
    asyncio.run(start_all())
