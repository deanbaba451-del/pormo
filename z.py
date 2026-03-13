import os, asyncio, re, threading
from telethon import TelegramClient, events, types, functions
from telethon.sessions import StringSession
from flask import Flask

# --- AYARLAR ---
API_ID = 35819402
API_HASH = '61cfbb3a501c02a69f2458a250de8c97'
STRING_SESSION = '1BJWap1sBux7heN05qZXV9kfJuHYDpsMJCgdluVZo2d1AXeS9vMDbQm-8a-DYv_CBrunyN_8eG8lqofKJ2lHGFaIXWq85pzlasy7g_eVaJT_-2e4KvLjGp5xn7VeSCxJ9UpZ2eMGyLtOGsHNZ0eL0fB7_a-aXfIROJU7qpxqJqly_OvKJ1iGEwVQRzsfWPQJLcBfVIdKTPuOHEjyRYYzn_f7_FS_s-WVesnW0DGo7Y2K0vpm1T_UHxXEuMNBjvtdjNvtCfm3i9RLYyl000u9zYahZJzMWifyKLCChtlWhDfLobdTsQhMvaLkCFVYvCyJYvuPvcdva-wXJd5-dFW8NLmY4b2fjeRo='

AUTHORIZED_USERS = [8256872080, 6534222591, 7727812432, 8343507331]
REPORT_RECEIVERS = [6534222591, 8256872080]
WHITE_LIST_CHANNELS = [-1003768699597, 1003768699597]
REQUIRED_BIO = ["@arabwstan", "t.me/arabwstan", "https://t.me/arabwstan"]

# Raporlananları hafızada tutmak için (Tekrar tekrar mesaj gelmesin diye)
reported_users = set()

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
app = Flask(__name__)

@app.route('/')
def home(): return "Sistem Aktif"

async def bio_checker():
    while True:
        try:
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    # Gruptaki adminleri ve yetkilileri çek
                    admins = [u.id for u in await client.get_participants(dialog.id, filter=types.ChannelParticipantsAdmins)]
                    
                    async for user in client.iter_participants(dialog.id, limit=100):
                        # EĞER: Bot ise, Admin ise veya Yetkili listendeyse ATLA
                        if user.bot or user.id in admins or user.id in AUTHORIZED_USERS:
                            continue
                        
                        # Zaten raporlandıysa bu turda atla
                        if user.id in reported_users:
                            continue

                        try:
                            full_user = await client(functions.users.GetFullUserRequest(user.id))
                            bio = full_user.full_user.about or ""
                            
                            # Bio hatalıysa
                            if not any(req in bio for req in REQUIRED_BIO):
                                mention = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
                                for admin_id in REPORT_RECEIVERS:
                                    await client.send_message(admin_id, f"Bio Hatası: {mention} kullanıcısının biosunda reklam yok.")
                                    await asyncio.sleep(2)
                                reported_users.add(user.id) # Hafızaya al
                            else:
                                # Biosunu düzelttiyse listeden çıkar (Tekrar hata yaparsa yine yakalasın)
                                if user.id in reported_users:
                                    reported_users.remove(user.id)
                        except: continue
            
            # Her taramadan sonra 5 dakika bekle (Sürekli tarayıp hesabı kısıtlatma)
            await asyncio.sleep(300) 
        except:
            await asyncio.sleep(60)

@client.on(events.NewMessage)
async def handler(event):
    if not event.chat: return
    sender_id = event.sender_id
    sender = await event.get_sender()

    if (sender and hasattr(sender, 'bot') and sender.bot) or sender_id in WHITE_LIST_CHANNELS or sender_id in AUTHORIZED_USERS:
        return

    # Reklam/Numara filtresi (Aynı kalıyor ama ince fontta)
    text = (event.raw_text or "").lower()
    if re.search(r'(?:\+90|0)?\s*[5]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}', text):
        await event.delete()
        rep = await event.respond(f"{sender.first_name} numara atmak yasak")
        await asyncio.sleep(5); await rep.delete()

async def start_bot():
    await client.start()
    asyncio.create_task(bio_checker())
    await client.run_until_disconnected()

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    asyncio.run(start_bot())
