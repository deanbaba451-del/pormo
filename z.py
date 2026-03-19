import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

api_id = 20275001
api_hash = "26e474f4a17fe5b306cc6ecfd2a1ed55"
session_string = "1BJWap1sBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
owners = [6534222591]

app = Flask('')

@app.route('/')
def home():
    return "bot aktif"

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run)
    t.start()

client = TelegramClient(StringSession(session_string), api_id, api_hash)
nuke_active = False

@client.on(events.NewMessage)
async def handler(event):
    global nuke_active
    sender = await event.get_sender()
    sender_id = event.sender_id

    if sender_id in owners:
        if event.text == ".b":
            nuke_active = True
            await event.edit("online")
            return
        elif event.text == ".i":
            nuke_active = False
            await event.edit("offline")
            return

    if nuke_active and sender_id not in owners:
        try:
            await event.delete()
        except:
            pass

async def main():
    keep_alive()
    print("bot baslatildi")
    await client.start()
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
