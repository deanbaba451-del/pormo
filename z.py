import asyncio
import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
# String'i tekrar temizledim
SESSION_STRING = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
SUPER_ADMIN = 6534222591

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Bağlantı hatasını yakalamak için try-except
try:
    client = TelegramClient(StringSession(SESSION_STRING.strip()), API_ID, API_HASH)
except Exception as e:
    print(f"BAĞLANTI HATASI: {e}")
    client = None

nuke_active = False

if client:
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
        if not nuke_active or event.sender_id == (await client.get_me()).id:
            return
        if event.text in ['.xon', '.xoff']:
            return
        try:
            await event.delete()
        except:
            pass

async def main():
    if client:
        await client.start()
        print("✅ BOT BAŞLADI!")
        await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    if client:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    else:
        import time
        while True: time.sleep(100)
