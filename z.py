import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
# Yeni aldığın sağlam session string:
SESSION_STRING = "1BJWap1sBu1W8QENXChVH0Lw5lc6libhNH0YH0Tsp7PJuoWJLuJCzwPhgrwuVeYBGvJE4yv4b1-EkE-aAW2a4JJ6t0zP9LBljeeMSuB_I7AFXL0OJl_LskVt8Dzynwoy7g1Gvqt5_PwEfeoR0tw-wiR12RiaLrruZREGXV8J5Lakm-bfczlP5fv7LJf2c2LoXe9dc-DzizVM_-Hd8GoB59nefVZmw9PaM5ethKzNeWSvLzxMAF9S8iZrBhQQwnYakCUOX40GfkYvlzgSkV8UmPBOX0687ZRvvkSl7ExdnYaJG2I26-BtgY6ZtqEeDokOf6ksxdH65LEH6JqZeac1_IuO9wKbIMLc="

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

    if event.sender_id is None or isinstance(event.sender, types.Channel):
        try: await event.delete()
        except: pass
        return

    is_command = any(text_raw.startswith(p) for p in PREFIX)
    
    if not is_command:
        if sender_id in AUTHORIZED_USERS: return
        if forward_protection.get(chat_id) and event.fwd_from:
            try: await event.delete()
            except: pass
            return
        if group_modes.get(chat_id) == "aktifchat":
            try: await event.delete()
            except: pass
            return
        if re.search(PHONE_PATTERN, text_raw.lower()) or re.search(LINK_PATTERN, text_raw.lower()):
            try:
                await event.delete()
                rep = await event.respond("seks anani sikerim")
                asyncio.create_task(self_destruct(rep))
            except: pass
            return
        if event.media and group_modes.get(chat_id) == "aktifmedya":
            if not (event.voice or event.video_note):
                try: await event.delete()
                except: pass
        return

    if sender_id in AUTHORIZED_USERS:
        parts = text_raw.split()
        cmd = parts[0][1:].lower() 
        args = parts[1:]
        response_text = None
        is_list_cmd = False 

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
            asyncio.create_task(self_destruct(event))
            if not is_list_cmd:
                asyncio.create_task(self_destruct(rep))

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
