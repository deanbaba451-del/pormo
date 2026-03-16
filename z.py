import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 33077604
API_HASH = '119992704d1dd27a6ebf9d3327189204'
STRING_SESSION = 'BAHMDn8AHs8rPUXaTCfTP6LEmzw6BXnQDWkaxHQsKbkZOB5OROG6FQx2lToH5Z2xN-TRX0GyJlAtxhHWF8NkcYoAIUQy6shKfsuHW1vGrhb0eRT-8FuI4FnMQSQjZgTMrwDOtyzyAh-W2MgSl13Ai4JX8vKIW3oyNnn_wQDrioFbCrqiivHzY95nTaeXoQDcqmaOjEL7uufxs1v2NsTyxzv3S3o5IqaOLJCRPoGpu0AO9Rx4zzQnvgu5ENxqEzmy6_b4bytzF8afsAILwwZGHcrr3V-HfzEzwCu8ibAYmkF00pdHxF1fAEo-oOt4BknJRuiHpxK7JwBH8CCclC2W-Bcfc6QcVAAAAAICU-dvAA'
BOT_TOKEN = "8753063580:AAHCUjFkDAGSAoWVMvp5cF6F6rTzryEsMMA"

SUPER_ADMIN = 6534222591
AUTHORIZED_USERS = [SUPER_ADMIN]

# --- DURUM VE HAFIZA ---
IS_ENABLED = True
message_store = {}
group_modes = {}

PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'
LINK_PATTERN = r'(?:t\.me|telegram\.me)\/\w+'

# İstemciler (Bot session'ı None yapıldı ki Render'da hata vermesin)
user_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
bot_client = TelegramClient(None, API_ID, API_HASH) # Bellekte çalışır, dosya yazmaz

app = Flask(__name__)

@app.route('/')
def home(): return "Sessiz Bot Guard Aktif"

def get_content_fingerprint(event):
    text = event.raw_text or ""
    media_id = "none"
    if event.media:
        if hasattr(event.media, 'photo'): media_id = f"ph_{event.media.photo.id}"
        elif hasattr(event.media, 'document'): media_id = f"doc_{event.media.document.id}"
    return f"{text}_{media_id}"

# --- USERBOT HANDLER ---
@user_client.on(events.NewMessage)
async def user_handler(event):
    global IS_ENABLED
    if not event.chat: return
    
    # Mesajı hafızaya al
    message_store[event.id] = get_content_fingerprint(event)
    if len(message_store) > 3000:
        message_store.pop(next(iter(message_store)))

    # Komut Kontrol
    if event.sender_id == SUPER_ADMIN:
        cmd = (event.raw_text or "").lower().strip()
        if cmd == "/editon":
            IS_ENABLED = True
            await event.delete()
        elif cmd == "/editoff":
            IS_ENABLED = False
            await event.delete()

# --- BOT HANDLER (Sessiz Silici) ---
@bot_client.on(events.MessageEdited)
async def bot_edit_handler(event):
    global IS_ENABLED
    if not IS_ENABLED: return
    if isinstance(event.media, types.MessageMediaGeo): return

    original = message_store.get(event.id)
    current = get_content_fingerprint(event)

    if not original or original == current: return
    
    protected = ["PLATE:", "ADMIN:", "UPDATE:", "STATUS:"]
    if any(word in (event.raw_text or "").upper() for word in protected): return

    try:
        # Silme işlemini TOKENLİ BOT yapar
        await bot_client.delete_messages(event.chat_id, event.id)
        message_store.pop(event.id, None)
    except:
        pass

async def main():
    # Başlatma işlemleri
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Sistem Başarıyla Başlatıldı!")
    
    # İki istemciyi aynı anda çalıştır
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == '__main__':
    # Flask (Web Server) ayrı bir kanalda çalışsın
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, use_reloader=False), daemon=True).start()
    
    # Ana asenkron döngüyü başlat
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
