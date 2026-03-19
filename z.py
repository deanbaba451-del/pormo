import os, threading, asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Bilgiler
api_id = 20275001
api_hash = "26e474f4a17fe5b306cc6ecfd2a1ed55"
string_session = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
owners = [6534222591]
active_chats = set()

# Flask (Render Portu İçin)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Aktif"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Bot
client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage(pattern=r"^\.b$", outgoing=True))
async def on(e):
    active_chats.add(e.chat_id)
    await e.edit("online")

@client.on(events.NewMessage(pattern=r"^\.i$", outgoing=True))
async def off(e):
    active_chats.discard(e.chat_id)
    await e.edit("offline")

@client.on(events.NewMessage)
async def del_msg(e):
    if e.chat_id in active_chats and e.sender_id not in owners and not e.out:
        try: await e.delete()
        except: pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    client.start()
    client.run_until_disconnected()
