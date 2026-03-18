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
SUPER_ADMIN = 6534222591

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Active"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

client = TelegramClient(StringSession(SESSION_STRING.strip()), API_ID, API_HASH)
nuke_active = False

# .b komutu -> online (SİLİNMEZ)
@client.on(events.NewMessage(pattern=r'\.b', chats=SUPER_ADMIN))
async def start_nuke(event):
    global nuke_active
    nuke_active = True
    await event.respond("online") # respond kullanarak yeni mesaj atar, edit yapmazsan silinmez

# .i komutu -> offline (SİLİNMEZ)
@client.on(events.NewMessage(pattern=r'\.i', chats=SUPER_ADMIN))
async def stop_nuke(event):
    global nuke_active
    nuke_active = False
    await event.respond("offline")

# NUKE SİSTEMİ
@client.on(events.NewMessage)
async def nuke_handler(event):
    global nuke_active
    me = await client.get_me()
    
    # 1. Eğer nuke kapalıysa bir şey yapma
    if not nuke_active:
        return
        
    # 2. Mesajı atan BİZSEK asla silme
    if event.sender_id == me.id:
        return

    # 3. Komutları ve cevapları koruma altına al (Çift kontrol)
    protected_texts = ['.b', '.i', 'online', 'offline']
    if event.text in protected_texts:
        return

    # 4. Diğer herkesin mesajını sil
    try:
        await event.delete()
    except:
        pass

async def main():
    await client.start()
    print("✅ Bot Başlatıldı! Komutlar: .b ve .i")
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
