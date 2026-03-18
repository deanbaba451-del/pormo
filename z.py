import os, asyncio, re, threading, time
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION_STRING = "1BJWap1sBu1W8QENXChVH0Lw5lc6libhNH0YH0Tsp7PJuoWJLuJCzwPhgrwuVeYBGvJE4yv4b1-EkE-aAW2a4JJ6t0zP9LBljeeMSuB_I7AFXL0OJl_LskVt8Dzynwoy7g1Gvqt5_PwEfeoR0tw-wiR12RiaLrruZREGXV8J5Lakm-bfczlP5fv7LJf2c2LoXe9dc-DzizVM_-Hd8GoB59nefVZmw9PaM5ethKzNeWSvLzxMAF9S8iZrBhQQwnYakCUOX40GfkYvlzgSkV8UmPBOX0687ZRvvkSl7ExdnYaJG2I26-BtgY6ZtqEeDokOf6ksxdH65LEH6JqZeac1_IuO9wKbIMLc="

SUPER_ADMIN = 6534222591
AUTHORIZED_USERS = [SUPER_ADMIN]
PREFIX = [".", "/"] 

PHONE_PATTERN = r'(?:\+|00)\d{1,4}\s?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}'
LINK_PATTERN = r'(?:t\.me|telegram\.me)\/(?:\+|joinchat|[\w-]+)'

group_modes = {} 
user_bans = {}   
media_bans = {}  

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "sistem aktif"

async def self_destruct(event, wait=4):
    await asyncio.sleep(wait)
    try: await event.delete()
    except: pass

async def timer_off(chat_id, mode, minutes):
    await asyncio.sleep(minutes * 60)
    if chat_id in group_modes and mode in group_modes[chat_id]:
        group_modes[chat_id].pop(mode)

# --- HERKES İÇİN MEDYA SİLME (2 DAKİKA) ---
async def auto_delete_media(event):
    await asyncio.sleep(120) 
    try: await event.delete()
    except: pass

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    chat_id = event.chat_id
    sender_id = event.sender_id
    text_raw = event.raw_text or ""
    
    is_command = any(text_raw.startswith(p) for p in PREFIX)
    is_auth = sender_id in AUTHORIZED_USERS
    modes = group_modes.get(chat_id, {})

    # 1. GENEL MEDYA TEMİZLİĞİ (Yetkili/Yetkisiz Herkes Dahil)
    if event.media:
        asyncio.create_task(auto_delete_media(event))

    # 2. KANAL / ANONİM KONTROLÜ
    if (event.sender_id is None or isinstance(event.sender, types.Channel)) and "con" in modes:
        try: return await event.delete()
        except: pass

    # 3. ÖZEL BAN KONTROLLERİ (Sadece yetkisizler için)
    if not is_auth:
        if sender_id in user_bans.get(chat_id, []):
            try: return await event.delete()
            except: pass
        
        if sender_id in media_bans.get(chat_id, []) and event.media:
            try: return await event.delete()
            except: pass

        # 4. FİLTRELER
        if not is_command:
            if "won" in modes:
                try: return await event.delete()
                except: pass

            if "ton" in modes:
                if re.search(PHONE_PATTERN, text_raw):
                    try:
                        await event.delete()
                        return await event.respond("mention sharing a phone number is prohibited.")
                    except: pass
                if re.search(LINK_PATTERN, text_raw.lower()):
                    try:
                        await event.delete()
                        return await event.respond("mention sharing groups or channels is prohibited.")
                    except: pass

            if "fwon" in modes and event.fwd_from:
                try: return await event.delete()
                except: pass

            if "xon" in modes and event.media:
                if not (event.voice or event.video_note):
                    try: return await event.delete()
                    except: pass

    # 5. YETKİLİ KOMUTLARI (Sadece AUTHORIZED_USERS)
    if is_auth and is_command:
        parts = text_raw.split()
        cmd = parts[0][1:].lower()
        args = parts[1:]
        res = None

        def get_duration():
            try: return int(args[0]) if args else None
            except: return None

        # Mod Komut Eşleşmeleri
        m_map = {
            "ton":"ton", "toff":"ton", 
            "xon":"xon", "xoff":"xon", 
            "won":"won", "woff":"won", 
            "con":"con", "coff":"con", 
            "fwon":"fwon", "fwoff":"fwon"
        }
        
        if cmd in m_map:
            mode_key = m_map[cmd]
            if chat_id not in group_modes: group_modes[chat_id] = {}
            
            if cmd.endswith("off"):
                group_modes[chat_id].pop(mode_key, None)
                res = f"{mode_key} offline"
            else:
                group_modes[chat_id][mode_key] = True
                res = f"{mode_key} online"
                dur = get_duration()
                if dur:
                    res += f" ({dur} min)"
                    asyncio.create_task(timer_off(chat_id, mode_key, dur))

        # Kişisel Ban Komutları
        elif cmd in ["tban", "tunban", "mban", "munban"]:
            target = None
            if event.is_reply:
                rep = await event.get_reply_message()
                target = rep.sender_id
            
            if target:
                if cmd == "tban":
                    if chat_id not in user_bans: user_bans[chat_id] = []
                    user_bans[chat_id].append(target)
                    res = "user text banned."
                elif cmd == "tunban":
                    if target in user_bans.get(chat_id, []): user_bans[chat_id].remove(target)
                    res = "user text ban lifted."
                elif cmd == "mban":
                    if chat_id not in media_bans: media_bans[chat_id] = []
                    media_bans[chat_id].append(target)
                    res = "user media banned."
                elif cmd == "munban":
                    if target in media_bans.get(chat_id, []): media_bans[chat_id].remove(target)
                    res = "user media ban lifted."

        if res:
            sent = await event.respond(res)
            asyncio.create_task(self_destruct(event))
            asyncio.create_task(self_destruct(sent))

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
