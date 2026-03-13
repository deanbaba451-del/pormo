import os, asyncio, re, threading
from telethon import TelegramClient, events, types, functions
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='

# Yeni owner eklendi
OWNERS = [6534222591, 8256872080, 8343507331]
AUTH = [8256872080, 6534222591, 7727812432, 8343507331]
WHITE_LIST = [-1003768699597]

locked_pp = {}
locked_name = {}
group_modes = {}

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "aktif"

HELP = """
.auth [id] - yetki ver
.unauth [id] - yetki al
.k - foto kilitle
.dk - foto ac
.n [isim] - isim kilitle
.dn - isim ac
.am - medya kapat
.dm - medya ac
.ac - chat kapat
.dc - chat ac
.c - komutlar
"""

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    sid = event.sender_id
    cid = event.chat_id
    txt = (event.raw_text or "").strip().lower()

    # OWNER ISLEMLERI
    if sid in OWNERS:
        if txt.startswith(".auth"):
            p = txt.split()
            if len(p) > 1 and p[1].isdigit():
                nid = int(p[1])
                if nid not in AUTH: AUTH.append(nid)
                await event.respond(f"{nid} yetkilendi")
        elif txt.startswith(".unauth"):
            p = txt.split()
            if len(p) > 1 and p[1].isdigit():
                tid = int(p[1])
                if tid in AUTH: AUTH.remove(tid)
                await event.respond(f"{tid} yetki alindi")

    # OZEL ID (.k, .n)
    if sid == 6534222591:
        if txt == ".k" and event.photo:
            locked_pp[cid] = await event.download_media(bytes)
            await event.respond("foto kilitlendi")
        elif txt == ".dk":
            locked_pp.pop(cid, None)
            await event.respond("foto kilidi acildi")
        elif txt.startswith(".n "):
            name = event.raw_text[3:].strip()
            locked_name[cid] = name
            await client(functions.channels.EditTitleRequest(channel=cid, title=name))
            await event.respond("isim kilitlendi")
        elif txt == ".dn":
            locked_name.pop(cid, None)
            await event.respond("isim kilidi acildi")

    # AUTH ISLEMLERI
    if sid in AUTH:
        if txt == ".c":
            await client.send_message("me", HELP)
            await event.delete()
        elif txt == ".am":
            group_modes[cid] = "am"
            await event.respond("medya kapali")
        elif txt == ".dm":
            group_modes.pop(cid, None)
            await event.respond("medya acik")
        elif txt == ".ac":
            group_modes[cid] = "ac"
            await event.respond("chat kapali")
        elif txt == ".dc":
            group_modes.pop(cid, None)
            await event.respond("chat acik")

    # FILTRELEME
    if sid not in AUTH and sid not in WHITE_LIST:
        mode = group_modes.get(cid)
        if mode == "ac":
            await event.delete()
            return
        if re.search(r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}', txt) or "@" in txt:
            await event.delete()
            return
        if event.media and mode == "am":
            if not (event.voice or event.audio or event.video_note):
                await event.delete()

@client.on(events.ChatAction)
async def protect(event):
    cid = event.chat_id
    if event.new_title and cid in locked_name:
        if event.new_title != locked_name[cid]:
            await client(functions.channels.EditTitleRequest(cid, locked_name[cid]))
    if event.new_photo and cid in locked_pp:
        await client(functions.channels.EditPhotoRequest(cid, await client.upload_file(locked_pp[cid])))

async def run():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    asyncio.run(run())
