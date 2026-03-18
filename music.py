import os
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# Ayarlar
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
ADMIN = 6534222591

app = Flask('')
@app.route('/')
def home():
    return "Bot Calisiyor"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

client = TelegramClient(None, API_ID, API_HASH).start(bot_token=None) # Session string kullanacak
nuke = False

@client.on(events.NewMessage(outgoing=True, pattern=r'\.b'))
async def b(e):
    global nuke
    nuke = True
    await e.edit("online")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.i'))
async def i(e):
    global nuke
    nuke = False
    await e.edit("offline")

@client.on(events.NewMessage)
async def temizle(e):
    global nuke
    if nuke and e.sender_id != ADMIN:
        try:
            await e.delete()
        except:
            pass

if __name__ == '__main__':
    Thread(target=run_flask).start()
    print("Bot baslatildi.")
    client.run_until_disconnected()
