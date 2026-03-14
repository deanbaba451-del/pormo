import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='

AUTHORIZED_USERS = [8256872080, 6534222591, 7727812432, 8305263080, 8343507331]
WHITE_LIST_CHANNELS = [-1003768699597, 1003768699597]

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
    sender_id = event.sender_id
    chat_id = event.chat_id
    sender = await event.get_sender()

    # 1. YÖNETİCİ KOMUTLARI (AUTHORIZED USERS)
    if sender_id in AUTHORIZED_USERS:
        text_cmd = (event.raw_text or "").lower().strip()
        if text_cmd == "/am":
            group_modes[chat_id] = "aktifmedya"
            return await event.respond("medya filtresi açıldı")
        elif text_cmd == "/dm":
            group_modes.pop(chat_id, None)
            return await event.respond("medya filtresi kapandı")
        elif text_cmd == "/ac":
            group_modes[chat_id] = "aktifchat"
            return await event.respond("chat kilitlendi")
        elif text_cmd == "/dc":
            group_modes.pop(chat_id, None)
            return await event.respond("chat açıldı")

    # 2. BEYAZ LİSTE VE MUAFİYETLER
    if (sender and hasattr(sender, 'bot') and sender.bot) or sender_id in WHITE_LIST_CHANNELS or sender_id in AUTHORIZED_USERS:
        return

    text = (event.raw_text or "").lower()
    current_mode = group_modes.get(chat_id)

    # 3. AKTİF CHAT (KİLİT) KONTROLÜ
    if current_mode == "aktifchat":
        try: await event.delete()
        except: pass
        return

    # 4. REKLAM VE NUMARA FİLTRESİ
    is_phone = re.search(PHONE_PATTERN, text)
    mentions = re.findall(MENTION_PATTERN, text)
    
    is_ad = False
    for m in mentions:
        try:
            entity = await client.get_entity(m)
            if isinstance(entity, (types.Channel, types.Chat)):
                is_ad = True
                break
        except: continue

    if is_phone or is_ad:
        try:
            await event.delete()
            u_name = f"@{sender.username}" if sender.username else sender.first_name
            reason = "numara atmak yasak" if is_phone else "reklam yasak"
            rep = await event.respond(f"{u_name} {reason}")
            await asyncio.sleep(5)
            await rep.delete()
        except: pass
        return

    # 5. MEDYA FİLTRESİ (/am modu)
    if event.media and current_mode == "aktifmedya":
        is_voice = event.voice or event.audio or event.video_note
        if not is_voice:
            try: await event.delete()
            except: pass

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(start_bot())
