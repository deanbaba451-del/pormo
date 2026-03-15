import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='
BOT_TOKEN = '7834488091:AAGKD8oKoU5duuniKSnqrIwMgX4B2aXIjt8'

OWNER_ID = 6534222591
AUTHORIZED_USERS = {8256872080, 8305263080, OWNER_ID}
SOURCE_CHANNEL_ID = -1003435930859 

# Filtreler
ANY_PHONE_PATTERN = r'\+?\d[\d\s\-]{7,15}' 
TG_LINK_PATTERN = r'(https?://)?t\.me/[^\s]+'
MENTION_PATTERN = r'@\w+'

is_spamming = {}

# İstemcileri Başlat
userbot = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
bot = TelegramClient('bot_worker', API_ID, API_HASH)

app = Flask(__name__)
@app.route('/')
def home(): return "Hibrit Sistem Aktif"

# --- USERBOT: GRUP POLİSİ VE TETİKLEYİCİ ---
@userbot.on(events.NewMessage)
async def userbot_handler(event):
    if not event.chat: return
    chat_id = event.chat_id
    sender_id = event.sender_id
    text = (event.raw_text or "")
    text_cmd = text.lower().strip()

    # 1. SPAM BAŞLAT/DURDUR (Sadece Yetkililer)
    if sender_id in AUTHORIZED_USERS:
        if text_cmd == "/sikis":
            await event.delete()
            if is_spamming.get(chat_id): return
            
            is_spamming[chat_id] = True
            info = await event.respond("🚀 sikis basladı")
            
            try:
                # Userbot kanaldaki mesajları listeler
                async for m in userbot.iter_messages(SOURCE_CHANNEL_ID, limit=100):
                    if not is_spamming.get(chat_id): break
                    if m.media:
                        # Bot üzerinden gruba gönderir (Hızlı ve güvenli)
                        await bot.send_file(chat_id, m.media)
                        await asyncio.sleep(0.3)
            finally:
                is_spamming[chat_id] = False
                await asyncio.sleep(5)
                await info.delete()
            return

        elif text_cmd == "/sekis":
            await event.delete()
            is_spamming[chat_id] = False
            msg = await event.respond("🛑 bosalma bitti")
            await asyncio.sleep(5)
            await msg.delete()
            return

    # 2. USERBOT REKLAM VE NUMARA FİLTRESİ
    if sender_id in AUTHORIZED_USERS: return

    is_phone = re.search(ANY_PHONE_PATTERN, text)
    is_tg_link = re.search(TG_LINK_PATTERN, text)
    
    if is_phone or is_tg_link:
        try:
            await event.delete() # Userbot mesajı siler
            u_name = (await event.get_sender()).first_name if event.sender else "Kullanıcı"
            reason = "numara yasak" if is_phone else "link yasak"
            rep = await event.respond(f"⚠️ {u_name}, {reason}")
            await asyncio.sleep(5)
            await rep.delete()
        except: pass

# --- ANA DÖNGÜ ---
async def start_all():
    # Userbot ve Botu aynı anda başlatıyoruz
    await userbot.start()
    await bot.start(bot_token=BOT_TOKEN)
    print("Sistem Aktif: Userbot denetliyor, Tokenli Bot basıyor.")
    await userbot.run_until_disconnected()

if __name__ == '__main__':
    # Flask Port Ayarı
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    # Event Loop
    asyncio.run(start_all())
