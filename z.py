import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 33077604
API_HASH = '119992704d1dd27a6ebf9d3327189204'
STRING_SESSION = 'BAHMDn8AHs8rPUXaTCfTP6LEmzw6BXnQDWkaxHQsKbkZOB5OROG6FQx2lToH5Z2xN-TRX0GyJlAtxhHWF8NkcYoAIUQy6shKfsuHW1vGrhb0eRT-8FuI4FnMQSQjZgTMrwDOtyzyAh-W2MgSl13Ai4JX8vKIW3oyNnn_wQDrioFbCrqiivHzY95nTaeXoQDcqmaOjEL7uufxs1v2NsTyxzv3S3o5IqaOLJCRPoGpu0AO9Rx4zzQnvgu5ENxqEzmy6_b4bytzF8afsAILwwZGHcrr3V-HfzEzwCu8ibAYmkF00pdHxF1fAEo-oOt4BknJRuiHpxK7JwBH8CCclC2W-Bcfc6QcVAAAAAICU-dvAA'

SUPER_ADMIN = 6534222591
AUTHORIZED_USERS = [SUPER_ADMIN]

# --- EDİT GUARD DEĞİŞKENLERİ ---
IS_ENABLED = True
message_store = {}

PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'
LINK_PATTERN = r'(?:t\.me|telegram\.me)\/\w+'
group_modes = {}

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

def get_content_fingerprint(event):
    text = event.raw_text or ""
    media_id = "none"
    if event.media:
        if hasattr(event.media, 'photo'): media_id = f"ph_{event.media.photo.id}"
        elif hasattr(event.media, 'document'): media_id = f"doc_{event.media.document.id}"
    return f"{text}_{media_id}"

@app.route('/')
def home(): return "Sessiz Muhafız Aktif"

# --- ANA HANDLER (Yeni Mesajlar ve Filtreler) ---
@client.on(events.NewMessage)
async def handler(event):
    global IS_ENABLED
    if not event.chat: return
    chat_id = event.chat_id
    sender_id = event.sender_id
    text_raw = event.raw_text or ""

    # Mesajı hafızaya al
    message_store[event.id] = get_content_fingerprint(event)
    if len(message_store) > 3000:
        message_store.pop(next(iter(message_store)))

    # Komutlar (Sadece SuperAdmin)
    if sender_id == SUPER_ADMIN:
        cmd = text_raw.lower().strip()
        if cmd == "/editon":
            IS_ENABLED = True
            await event.delete()
            return
        elif cmd == "/editoff":
            IS_ENABLED = False
            await event.delete()
            return

    # Yönetici Komutları
    if sender_id in AUTHORIZED_USERS:
        cmd = text_raw.lower().strip()
        if cmd == "/am": group_modes[chat_id] = "aktifmedya"
        elif cmd == "/dm": group_modes.pop(chat_id, None)
        elif cmd == "/ac": group_modes[chat_id] = "aktifchat"
        elif cmd == "/dc": group_modes.pop(chat_id, None)

    # Muafiyet
    sender = await event.get_sender()
    if sender_id in AUTHORIZED_USERS or (sender and hasattr(sender, 'bot') and sender.bot):
        return

    # Reklam ve Medya Filtreleri (Sessiz Silme)
    if group_modes.get(chat_id) == "aktifchat":
        try: await event.delete()
        except: pass
        return

    if re.search(PHONE_PATTERN, text_raw) or re.search(LINK_PATTERN, text_raw.lower()) or event.fwd_from:
        try: await event.delete()
        except: pass

# --- EDİT HANDLER (Sessiz Edit Guard) ---
@client.on(events.MessageEdited)
async def handle_edits(event):
    global IS_ENABLED
    if not IS_ENABLED: return
    if isinstance(event.media, types.MessageMediaGeo): return

    original = message_store.get(event.id)
    current = get_content_fingerprint(event)

    if original and original == current: return
    
    # Korumalı kelimeler (Editlense bile silinmez)
    protected = ["PLATE:", "ADMIN:", "UPDATE:", "STATUS:"]
    txt_upper = (event.raw_text or "").upper()
    if any(word in txt_upper for word in protected): return

    try:
        # Sessizce sil
        await event.delete()
        message_store.pop(event.id, None)
    except:
        pass

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    client.loop.run_until_complete(start_bot())
