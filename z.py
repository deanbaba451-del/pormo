import os, asyncio, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights

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

# --- ANTİ-BOT & ANTİ-ADMİN BOT ---
@client.on(events.ChatAction)
async def protector(event):
    # 1. Normal Katılma/Eklenme Durumu
    if event.user_joined or event.user_added:
        u_list = await event.get_users()
        if not isinstance(u_list, list): u_list = [u_list]
        for u in u_list:
            if u.bot:
                try:
                    await client(EditBannedRequest(event.chat_id, u.id, ChatBannedRights(until_date=None, view_messages=True)))
                    print(f"✅ ÜYE BOT BANLANDI: {u.first_name}")
                except Exception as e: print(f"❌ BAN HATASI: {e}")

    # 2. BOT YÖNETİCİ YAPILIRSA (Yetki Değişimi)
    elif event.new_pin or (event.action_message and isinstance(event.action_message.action, types.MessageActionChatEditAdmin)):
        # Gruptaki admin listesini tazele ve bot var mı bak
        async for admin in client.iter_participants(event.chat_id, filter=types.ChannelParticipantsAdmins):
            if admin.bot and admin.id != (await client.get_me()).id:
                try:
                    # Botun adminliğini al (Tüm yetkileri False yap)
                    await client(EditAdminRequest(event.chat_id, admin.id, ChatAdminRights(
                        post_messages=False, add_admins=False, invite_users=False, change_info=False,
                        ban_users=False, delete_messages=False, pin_messages=False, manage_call=False
                    ), rank="Yasak"))
                    # Ardından banla
                    await client(EditBannedRequest(event.chat_id, admin.id, ChatBannedRights(until_date=None, view_messages=True)))
                    print(f"🚫 ADMİN BOT ALINDI VE BANLANDI: {admin.first_name}")
                except Exception as e: print(f"❌ ADMİN BOT HATASI: {e}")

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    chat_id = event.chat_id
    sender_id = event.sender_id
    text_raw = event.raw_text or ""
    
    is_auth = sender_id in OWNERS
    is_command = any(text_raw.startswith(p) for p in PREFIX)

    if chat_lock.get(chat_id) and not is_auth:
        try: await event.delete()
        except: pass
        return

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
    print("🚀 Koruma Sistemi Aktif!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
