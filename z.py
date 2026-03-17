import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
SESSION_STRING = "BAE1XzkAQODlnE7Q5p49txSKPSdxVCdBv4ZnzUE1TGF9OGngoeZSgUoNg9AXyPbRMgmDsQ0hoyv9fVy8JnEu0SUs6DkcQ5i6GqNlQnfXM3pbMr4JNx8KilGKWgUcoU8FQm5EiWRQVTL-1xXGx1TxkoR_UYXeycIqvL4uVwvDSAVRaRCbwKgafBL49WPXoWq0HVpP46YBlT0ocjTeHIOUBKtnoAGQMQL079ok91BSbMOH0GXritBykHeCispbLyzRNt4KmSpLZlEKzkxlicYTvdDaPOzvmZRnnIUoASoi2YSCwe4Le0sR0YZ-P_5GvN-vm8CdmWa947-_ZSVxuCvGSXniz8yeFQAAAAHfRBiOAA"

SUPER_ADMIN = 6534222591
AUTHORIZED_USERS = [SUPER_ADMIN]
PREFIX = [".", "/"] 

PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'
LINK_PATTERN = r'(?:t\.me|telegram\.me)\/\w+'

group_modes = {}
forward_protection = {} 

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "sistem aktif"

# Mesajları 4 saniye sonra silen yardımcı fonksiyon
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

    # 1. KANAL/ANONİM ENGELLE (Sessiz)
    if event.sender_id is None or isinstance(event.sender, types.Channel):
        try: await event.delete()
        except: pass
        return

    # Prefix Kontrolü
    is_command = any(text_raw.startswith(p) for p in PREFIX)
    
    # 2. KOMUT DEĞİLSE FİLTRELERİ ÇALIŞTIR
    if not is_command:
        if sender_id in AUTHORIZED_USERS: return
        
        # Forward Koruması (Sessiz)
        if forward_protection.get(chat_id) and event.fwd_from:
            try: await event.delete()
            except: pass
            return

        # Chat Kilidi (.won)
        if group_modes.get(chat_id) == "aktifchat":
            try: await event.delete()
            except: pass
            return

        # Reklam/Link (Küfürlü Tepki + 4sn Silme)
        if re.search(PHONE_PATTERN, text_raw.lower()) or re.search(LINK_PATTERN, text_raw.lower()):
            try:
                await event.delete()
                rep = await event.respond("seks anani sikerim")
                asyncio.create_task(self_destruct(rep))
            except: pass
            return

        # Medya Filtresi (.xon)
        if event.media and group_modes.get(chat_id) == "aktifmedya":
            if not (event.voice or event.video_note):
                try: await event.delete()
                except: pass
        return

    # 3. YETKİLİ KOMUTLARI
    if sender_id in AUTHORIZED_USERS:
        parts = text_raw.split()
        cmd = parts[0][1:].lower() 
        args = parts[1:]
        response_text = None
        is_list_cmd = False 

        # --- YETKİ YÖNETİMİ ---
        if sender_id == SUPER_ADMIN:
            target_id = None
            if event.is_reply:
                reply = await event.get_reply_message()
                target_id = reply.sender_id
            elif args:
                try:
                    user_entity = await client.get_entity(args[0])
                    target_id = user_entity.id
                except: pass

            if cmd == "auth" and target_id:
                if target_id not in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.append(target_id)
                    try:
                        u = await client.get_entity(target_id)
                        name = f"[{u.first_name.lower()}](tg://user?id={u.id})"
                    except: name = f"`{target_id}`"
                    response_text = f"{name} authorized."
            
            elif cmd == "deauth" and target_id:
                if target_id != SUPER_ADMIN and target_id in AUTHORIZED_USERS:
                    AUTHORIZED_USERS.remove(target_id)
                    try:
                        u = await client.get_entity(target_id)
                        name = f"[{u.first_name.lower()}](tg://user?id={u.id})"
                    except: name = f"`{target_id}`"
                    response_text = f"{name} authority has been taken."

            elif cmd == "authlist":
                is_list_cmd = True
                auth_list_text = "authorized users list:\n\n"
                for uid in AUTHORIZED_USERS:
                    try:
                        u = await client.get_entity(uid)
                        auth_list_text += f"user: {u.first_name.lower()} | id: `{u.id}`\n"
                    except: 
                        auth_list_text += f"user: authorized | id: `{uid}`\n"
                response_text = auth_list_text

        # --- MOD KOMUTLARI ---
        if cmd == "xon":
            group_modes[chat_id] = "aktifmedya"
            response_text = "online"
        elif cmd == "xoff":
            group_modes.pop(chat_id, None)
            response_text = "offline"
        elif cmd == "won":
            group_modes[chat_id] = "aktifchat"
            response_text = "online"
        elif cmd == "woff":
            group_modes.pop(chat_id, None)
            response_text = "offline"
        elif cmd == "forwardon":
            forward_protection[chat_id] = True
            response_text = "online"
        elif cmd == "forwardoff":
            forward_protection[chat_id] = False
            response_text = "offline"

        if response_text:
            rep = await event.respond(response_text)
            # Komut mesajını her zaman sil (4 sn)
            asyncio.create_task(self_destruct(event))
            
            # Eğer authlist DEĞİLSE yanıtı da sil (4 sn)
            if not is_list_cmd:
                asyncio.create_task(self_destruct(rep))

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
