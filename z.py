import os
import asyncio
import re
import threading
import base64
import requests
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='
XAI_API_KEY = "APIKEY"

AUTHORIZED_USERS = [8256872080, 6534222591, 7727812432, 8343507331]

PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'
MENTION_PATTERN = r'@\w+'

group_modes = {}
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "Sistem Aktif"

def check_nsfw_with_grok(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-vision-beta",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Does this image contain NSFW, nudity, weapons, or drugs? Answer only 'yes' or 'no'."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}]
        }
        response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        return "yes" in response.json()['choices'][0]['message']['content'].lower()
    except: return False

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    sender_id = event.sender_id
    chat_id = event.chat_id
    sender = await event.get_sender()
    
    # OWNER MUAFİYETİ
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
        return

    text = (event.raw_text or "").lower()
    current_mode = group_modes.get(chat_id)

    # 1. CHAT KİLİDİ
    if current_mode == "aktifchat":
        try: await event.delete()
        except: pass
        return

    # 2. NUMARA SİLİCİ
    if re.search(PHONE_PATTERN, text):
        try:
            await event.delete()
            rep = await event.respond(f"@{sender.username if sender.username else sender_id} numara atmak yasak")
            await asyncio.sleep(5)
            await rep.delete()
        except: pass
        return

    # 3. REKLAM (GRUP/KANAL) SİLİCİ
    mentions = re.findall(MENTION_PATTERN, text)
    for m in mentions:
        try:
            entity = await client.get_entity(m)
            if isinstance(entity, (types.Channel, types.Chat)):
                await event.delete()
                rep = await event.respond(f"@{sender.username if sender.username else sender_id} reklam yasak")
                await asyncio.sleep(5)
                await rep.delete()
                return
        except: pass

    # 4. MEDYA VE GROK NSFW ANALİZİ
    if event.media:
        if current_mode == "aktifmedya":
            is_voice = event.voice or event.audio or event.video_note
            if not is_voice:
                try: await event.delete()
                except: pass
                return

        if event.photo or event.sticker:
            file_path = await event.download_media()
            is_bad = await asyncio.to_thread(check_nsfw_with_grok, file_path)
            if os.path.exists(file_path): os.remove(file_path)
            
            if is_bad:
                try:
                    await event.delete()
                    rep = await event.respond(f"@{sender.username if sender.username else sender_id} uygunsuz görsel")
                    await asyncio.sleep(5)
                    await rep.delete()
                except: pass

async def main():
    await client.start()
    print("Sistem Grok API ve Otomatik Temizleme ile Aktif!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))), daemon=True).start()
    asyncio.run(main())
