import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# AYARLAR
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
ADMIN = 6534222591

app = Flask('')
active_chats = set()
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@app.route('/')
def home():
    return "active"

@client.on(events.NewMessage(pattern=r'\.b'))
async def b_handler(e):
    if e.out or e.sender_id == ADMIN:
        active_chats.add(e.chat_id)
        await e.edit("online")

@client.on(events.NewMessage(pattern=r'\.i'))
async def i_handler(e):
    if e.out or e.sender_id == ADMIN:
        if e.chat_id in active_chats:
            active_chats.remove(e.chat_id)
        await e.edit("offline")

@client.on(events.NewMessage)
async def temizle(e):
    # Eğer chat listedeyse ve mesajı atan sen veya admin değilsen SİL
    if e.chat_id in active_chats:
        if not e.out and e.sender_id != ADMIN:
            try:
                await e.delete()
            except:
                pass

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start())
    print("Bot calisiyor...")
    loop.run_forever()

if __name__ == '__main__':
    # Botu ayrı thread'de başlatıyoruz
    Thread(target=run_bot, daemon=True).start()
    # Flask ana thread'de çalışıyor (Render bunu bekler)
    app.run(host='0.0.0.0', port=8080)
