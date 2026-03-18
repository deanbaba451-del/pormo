import asyncio
import os
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
ADMIN = 6534222591

app = Flask('')
nuke = False

@app.route('/')
def home():
    return "online"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Botu global tanımla
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.b'))
async def b_handler(e):
    global nuke
    nuke = True
    await e.edit("online")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.i'))
async def i_handler(e):
    global nuke
    nuke = False
    await e.edit("offline")

@client.on(events.NewMessage)
async def temizleyici(e):
    global nuke
    # Nuke açıkken ve mesajı atan sen değilsen (veya süper admin değilse) sil
    if nuke and e.sender_id != ADMIN:
        try:
            await e.delete()
        except:
            pass

async def start_bot():
    await client.start()
    print("Bot hazir!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Flask'ı arka planda başlat
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Botu ana döngüde çalıştır
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
