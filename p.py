import asyncio
import os
import threading
import time
import requests
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION_STRING = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
SUPER_ADMIN = 6534222591

# --- FLASK & UYUTMAMA SİSTEMİ ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active and Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Botun uyumasını engellemek için kendi URL'sine ping atar
def keep_alive():
    url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}.onrender.com"
    while True:
        try:
            requests.get(url)
            print("Ping atıldı, bot uyanık tutuluyor.")
        except: pass
        time.sleep(600) # 10 dakikada bir

# --- TELEGRAM BOT ---
client = TelegramClient(StringSession(SESSION_STRING.strip()), API_ID, API_HASH)
active_chats = set()

# .b komutu -> Sadece yazılan sohbeti AÇAR (online)
@client.on(events.NewMessage(pattern=r'\.b'))
async def start_nuke(event):
    if event.sender_id != SUPER_ADMIN: return
    chat_id = event.chat_id
    if chat_id not in active_chats:
        active_chats.add(chat_id)
        await event.respond("online")

# .i komutu -> Sadece yazılan sohbeti KAPATIR (offline)
@client.on(events.NewMessage(pattern=r'\.i'))
async def stop_nuke(event):
    if event.sender_id != SUPER_ADMIN: return
    chat_id = event.chat_id
    if chat_id in active_chats:
        active_chats.remove(chat_id)
        await event.respond("offline")

# NUKE İŞLEMCİSİ
@client.on(events.NewMessage)
async def nuke_handler(event):
    chat_id = event.chat_id
    if chat_id not in active_chats: return
    
    me = await client.get_me()
    # Kendi mesajlarımızı veya komutları ASLA silme
    if event.sender_id == me.id or event.text in ['.b', '.i', 'online', 'offline']:
        return

    try:
        await event.delete()
    except Exception as e:
        print(f"Silme hatası (Yetki yok?): {e}")

async def main():
    try:
        await client.start()
        print("✅ BOT BAŞARIYLA BAĞLANDI!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"KRİTİK HATA: {e}")

if __name__ == "__main__":
    # Flask ve Keep-Alive thread'lerini başlat
    threading.Thread(target=run_flask, daemon=True).start()
    if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
        threading.Thread(target=keep_alive, daemon=True).start()
    
    # Botu başlat
    asyncio.run(main())
