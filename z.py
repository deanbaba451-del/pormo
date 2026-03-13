import os, asyncio, re, threading
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='

# Yetkili ID'leri
AUTHORIZED_USERS = [8256872080, 6534222591, 7727812432, 8343507331]
# Muaf tutulacak kanallar/gruplar
WHITE_LIST_CHANNELS = [-1003768699597, 1003768699597]

PHONE_PATTERN = r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'
MENTION_PATTERN = r'@\w+'

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "Sistem Aktif"

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    sender_id = event.sender_id
    sender = await event.get_sender()

    # BEYAZ LİSTE KONTROLÜ
    # Eğer yazan bir bot ise, yetkili ise veya beyaz listedeki kanal ise dokunma
    if (sender and hasattr(sender, 'bot') and sender.bot) or sender_id in WHITE_LIST_CHANNELS or sender_id in AUTHORIZED_USERS:
        return

    text = (event.raw_text or "").lower()

    # REKLAM VE NUMARA KONTROLÜ
    is_phone = re.search(PHONE_PATTERN, text)
    mentions = re.findall(MENTION_PATTERN, text)
    
    is_ad = False
    for m in mentions:
        try:
            # Etiketlenen şey bir Kanal veya Grup mu bak
            entity = await client.get_entity(m)
            if isinstance(entity, (types.Channel, types.Chat)):
                is_ad = True
                break
        except:
            continue

    if is_phone or is_ad:
        try:
            await event.delete()
            u_name = f"@{sender.username}" if sender.username else sender.first_name
            reason = "numara atmak yasak" if is_phone else "reklam yasak"
            
            # İnce fontta cevap
            rep = await event.respond(f"{u_name} {reason}")
            
            # 5 saniye sonra uyarıyı temizle
            await asyncio.sleep(5)
            await rep.delete()
        except:
            pass

async def start_bot():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Flask sunucusunu ayrı bir koldan başlat
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port), daemon=True).start()
    
    # Botu başlat
    asyncio.run(start_bot())
