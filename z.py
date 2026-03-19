import os, asyncio, threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION_STRING = "1BJWap1sBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="

OWNERS = [6534222591]
PREFIX = ["/"] # Sadece / prefix'i

# Sohbet kilidi durumu (chat_id: True/False)
chat_lock = {}

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "sistem aktif"

async def self_destruct(event, wait=4):
    await asyncio.sleep(wait)
    try: await event.delete()
    except: pass

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    chat_id = event.chat_id
    sender_id = event.sender_id
    text_raw = event.raw_text or ""
    
    is_auth = sender_id in OWNERS
    is_command = any(text_raw.startswith(p) for p in PREFIX)

    # 1. SOHBET KİLİDİ KONTROLÜ
    # Eğer bu grup kilitliyse ve yazan kişi yetkili değilse mesajı sil
    if chat_lock.get(chat_id) and not is_auth:
        try:
            await event.delete()
            return
        except: pass

    # 2. KOMUTLAR (Sadece Yetkililer İçin)
    if is_auth and is_command:
        cmd = text_raw[1:].lower().strip() # Başındaki / işaretini atar

        if cmd == "won":
            chat_lock[chat_id] = True
            sent = await event.respond("on.")
            asyncio.create_task(self_destruct(event)) # Komutu sil
            asyncio.create_task(self_destruct(sent))  # Yanıtı sil
            
        elif cmd == "woff":
            chat_lock[chat_id] = False
            sent = await event.respond("off.")
            asyncio.create_task(self_destruct(event)) # Komutu sil
            asyncio.create_task(self_destruct(sent))  # Yanıtı sil

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
