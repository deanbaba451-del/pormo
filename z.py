import asyncio
import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION_STRING = "BAE1XzkAQODlnE7Q5p49txSKPSdxVCdBv4ZnzUE1TGF9OGngoeZSgUoNg9AXyPbRMgmDsQ0hoyv9fVy8JnEu0SUs6DkcQ5i6GqNlQnfXM3pbMr4JNx8KilGKWgUcoU8FQm5EiWRQVTL-1xXGx1TxkoR_UYXeycIqvL4uVwvDSAVRaRCbwKgafBL49WPXoWq0HVpP46YBlT0ocjTeHIOUBKtnoAGQMQL079ok91BSbMOH0GXritBykHeCispbLyzRNt4KmSpLZlEKzkxlicYTvdDaPOzvmZRnnIUoASoi2YSCwe4Le0sR0YZ-P_5GvN-vm8CdmWa947-_ZSVxuCvGSXniz8yeFQAAAAHfRBiOAA"
SUPER_ADMIN = 6534222591

# --- FLASK KURULUMU (Render İçin) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Online!"

def run_flask():
    # Render'ın verdiği portu al, yoksa 8080 kullan
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT KURULUMU ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
nuke_active = False

@client.on(events.NewMessage(pattern=r'\.xon'))
async def start_nuke(event):
    global nuke_active
    if event.sender_id == SUPER_ADMIN:
        nuke_active = True
        await event.edit("🚀 **online**")

@client.on(events.NewMessage(pattern=r'\.xoff'))
async def stop_nuke(event):
    global nuke_active
    if event.sender_id == SUPER_ADMIN:
        nuke_active = False
        await event.edit("🛑 **offline**")

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
    print("Bot başlatılıyor...")
    await client.start()
    print("Bot aktif! Komutlar: .xon / .xoff")
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Flask'ı ayrı bir thread'de (iş parçacığında) başlat
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Telegram Botu ana döngüde başlat
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
