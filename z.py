import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='

# Sadece bu ID yetki yönetebilir (/auth, /unauth)
SUPER_ADMIN = 6534222591
AUTHORIZED_USERS = [SUPER_ADMIN]

PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'
MENTION_PATTERN = r'@\w+'

group_modes = {}
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "Sistem Aktif"

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    chat_id = event.chat_id
    sender_id = event.sender_id
    text_raw = event.raw_text or ""

    # --- 1. KANAL ENGELLEME (Sessiz) ---
    # Mesaj bir kanal üzerinden (anonim veya bağlı kanal) geliyorsa direkt siler.
    if event.sender_id is None or isinstance(event.sender, types.Channel):
        try:
            await event.delete()
            return # Kanal mesajı olduğu için diğer işlemlere bakma
        except: pass

    # --- 2. YETKİ YÖNETİMİ (Sadece SUPER_ADMIN) ---
    if sender_id == SUPER_ADMIN:
        if text_raw.startswith("/auth") and event.is_reply:
            reply = await event.get_reply_message()
            u_id = reply.sender_id
            if u_id not in AUTHORIZED_USERS:
                AUTHORIZED_USERS.append(u_id)
                return await event.respond(f"seks yt oldu")
        
        elif text_raw.startswith("/unauth") and event.is_reply:
            reply = await event.get_reply_message()
            u_id = reply.sender_id
            if u_id != SUPER_ADMIN and u_id in AUTHORIZED_USERS:
                AUTHORIZED_USERS.remove(u_id)
                return await event.respond(f"seks ytsi gitti")

    # --- 3. YÖNETİCİ KOMUTLARI ---
    if sender_id in AUTHORIZED_USERS:
        cmd = text_raw.lower().strip()
        if cmd == "/am":
            group_modes[chat_id] = "aktifmedya"
            return await event.respond("seks aktif")
        elif cmd == "/dm":
            group_modes.pop(chat_id, None)
            return await event.respond("seksler kapandı")
        elif cmd == "/ac":
            group_modes[chat_id] = "aktifchat"
            return await event.respond("seks kapandı")
        elif cmd == "/dc":
            group_modes.pop(chat_id, None)
            return await event.respond("seks açıldı")

    # --- 4. MUAFİYET (Adminler ve Botlar) ---
    sender = await event.get_sender()
    if sender_id in AUTHORIZED_USERS or (sender and hasattr(sender, 'bot') and sender.bot):
        return

    # --- 5. AKTİF CHAT KİLİDİ ---
    current_mode = group_modes.get(chat_id)
    if current_mode == "aktifchat":
        try: await event.delete()
        except: pass
        return

    # --- 6. REKLAM VE NUMARA FİLTRESİ ---
    text_lower = text_raw.lower()
    if re.search(PHONE_PATTERN, text_lower) or re.search(MENTION_PATTERN, text_lower):
        try:
            await event.delete()
            rep = await event.respond("no number tm?")
            await asyncio.sleep(3)
            await rep.delete()
        except: pass
        return

    # --- 7. MEDYA FİLTRESİ (/am modu) ---
    if event.media and current_mode == "aktifmedya":
        # Ses kaydı ve yuvarlak video hariç her şeyi siler
        if not (event.voice or event.video_note):
            try: await event.delete()
            except: pass

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
