import os, asyncio, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION_STRING = "1BJWap1sBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="

OWNERS = [6534222591]
PREFIX = ["/"]

chat_lock = {}

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "sistem aktif"

async def self_destruct(event, wait=4):
    await asyncio.sleep(wait)
    try: await event.delete()
    except: pass

# --- ANTİ-BOT ÖZELLİĞİ ---
@client.on(events.ChatAction)
async def bot_blocker(event):
    # Eğer yeni bir kullanıcı katıldıysa veya eklendiyse
    if event.user_joined or event.user_added:
        users = await event.get_users()
        for user in users:
            # Eğer eklenen kullanıcı bir BOT ise
            if user.bot:
                try:
                    # Botu gruptan banla (Kick de yapılabilir ama ban kesin çözümdür)
                    await client.edit_permissions(event.chat_id, user.id, view_messages=False)
                except Exception as e:
                    print(f"Bot banlanamadı: {e}")

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    chat_id = event.chat_id
    sender_id = event.sender_id
    text_raw = event.raw_text or ""
    
    is_auth = sender_id in OWNERS
    is_command = any(text_raw.startswith(p) for p in PREFIX)

    # 1. SOHBET KİLİDİ
    if chat_lock.get(chat_id) and not is_auth:
        try:
            await event.delete()
            return
        except: pass

    # 2. KOMUTLAR
    if is_auth and is_command:
        cmd = text_raw[1:].lower().strip()

        if cmd == "won":
            chat_lock[chat_id] = True
            sent = await event.respond("on.")
            asyncio.create_task(self_destruct(event))
            asyncio.create_task(self_destruct(sent))
            
        elif cmd == "woff":
            chat_lock[chat_id] = False
            sent = await event.respond("off.")
            asyncio.create_task(self_destruct(event))
            asyncio.create_task(self_destruct(sent))

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
