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

# SENİN ID'N BURADA SABİTLENDİ
MY_ID = 6534222591

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

client = TelegramClient(StringSession(SESSION_STRING.strip()), API_ID, API_HASH)
active_chats = set()

# .b komutu -> Sadece sen yazınca çalışır
@client.on(events.NewMessage(pattern=r'\.b'))
async def start_nuke(event):
    if event.sender_id == MY_ID:
        active_chats.add(event.chat_id)
        await event.respond("online")

# .i komutu -> Sadece sen yazınca çalışır
@client.on(events.NewMessage(pattern=r'\.i'))
async def stop_nuke(event):
    if event.sender_id == MY_ID:
        if event.chat_id in active_chats:
            active_chats.remove(event.chat_id)
        await event.respond("offline")

# NUKE İŞLEMCİSİ
@client.on(events.NewMessage)
async def nuke_handler(event):
    # Bu sohbet listede yoksa hiçbir şey yapma
    if event.chat_id not in active_chats:
        return

    # MESAJI ATAN SENSEN (MY_ID) ASLA SİLME
    if event.sender_id == MY_ID:
        return

    # Botun kendi attığı mesajları (online/offline) koru
    me = await client.get_me()
    if event.sender_id == me.id:
        return
    
    # Komut metinlerini içeren mesajları silme
    if event.text in ['.b', '.i', 'online', 'offline']:
        return

    # Geri kalan herkesin mesajını sil
    try:
        await event.delete()
    except Exception as e:
        print(f"Silme hatası: {e}")

async def main():
    await client.start()
    print(f"✅ Bot Aktif! Sahip ID: {MY_ID}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
