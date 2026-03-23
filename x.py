import asyncio
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, executor
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.channels import InviteToChannelRequest

# --- RENDER PORT AYARI (Flask) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot Aktif!", 200

def run_flask():
    # Render'ın verdiği portu kullan, yoksa 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT AYARLARI ---
BOT_TOKEN = "8730162607:AAFI6HgBuvcgRon71Js7vo5c-trSsFMPd0k"
OWNER_ID = 8256872080

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

allowed_users = {OWNER_ID}
sessions = {}
running = {}

def log(text):
    print(text)
    with open("log.txt", "a") as f:
        f.write(text + "\n")

def is_allowed(uid):
    return uid in allowed_users

# --- KOMUTLAR ---

@dp.message_handler(commands=["yetki"])
async def yetki(msg: types.Message):
    if msg.from_user.id != OWNER_ID: return
    try:
        _, act, uid = msg.text.split()
        uid = int(uid)
        if act == "ekle":
            allowed_users.add(uid)
            await msg.reply(f"✅ {uid} yetkilendirildi")
        elif act == "sil":
            allowed_users.discard(uid)
            await msg.reply(f"⛔ {uid} yetki kaldırıldı")
    except:
        await msg.reply("Kullanım: /yetki ekle 12345")

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if not is_allowed(msg.from_user.id):
        return await msg.reply("❌ Yetkin yok")
    await msg.reply("📱 Telefon numaranı gönder (+905xx...)")

@dp.message_handler(lambda m: m.text.startswith("+"))
async def phone(msg: types.Message):
    if not is_allowed(msg.from_user.id): return
    
    # BURAYI KENDİ BİLGİLERİNLE DOLDUR
    MY_API_ID = 1234567 
    MY_API_HASH = "buraya_api_hash_yaz"
    
    client = TelegramClient(f"session_{msg.from_user.id}", MY_API_ID, MY_API_HASH)
    await client.connect()
    try:
        await client.send_code_request(msg.text)
        sessions[msg.from_user.id] = {"client": client, "phone": msg.text}
        await msg.reply("📩 Kod gönderildi, lütfen 5 haneli kodu yaz:")
    except Exception as e:
        await msg.reply(f"❌ Hata: {e}")

@dp.message_handler(lambda m: m.text.isdigit() and len(m.text) in [5,6])
async def code(msg: types.Message):
    uid = msg.from_user.id
    if uid not in sessions or not is_allowed(uid): return
    
    s = sessions[uid]
    try:
        await s["client"].sign_in(s["phone"], msg.text)
        await msg.reply("✅ Giriş başarılı! Grupları çekiyorum...")
        await show_groups(msg, s["client"])
    except SessionPasswordNeededError:
        await msg.reply("🔒 2FA şifreni gönder:")
        s["await_2fa"] = True
    except Exception as e:
        await msg.reply(f"❌ Hata: {e}")

async def show_groups(msg, client):
    dialogs = await client.get_dialogs()
    text = "📌 Grupların:\n"
    sessions[msg.from_user.id]["dialogs"] = []
    count = 1
    for d in dialogs:
        if d.is_group or d.is_channel:
            text += f"{count}. {d.name}\n"
            sessions[msg.from_user.id]["dialogs"].append(d)
            count += 1
            if count > 15: break # Mesaj çok uzun olmasın
    text += "\nBaşlamak için: /basla [numara]"
    await msg.reply(text)

@dp.message_handler(commands=["basla"])
async def basla(msg: types.Message):
    uid = msg.from_user.id
    if not is_allowed(uid) or uid not in sessions: return
    
    try:
        idx = int(msg.text.split()[1]) - 1
        group = sessions[uid]["dialogs"][idx]
        running[uid] = True
        await msg.reply(f"🚀 {group.name} grubuna ekleme başladı...")
        
        # Örnek kullanıcı listesi
        users_to_add = ["kullanici1", "kullanici2"] 
        
        while running.get(uid):
            try:
                await sessions[uid]["client"](InviteToChannelRequest(group, users_to_add))
                log(f"{uid} ekleme yaptı.")
                await asyncio.sleep(60)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception as e:
                log(f"Hata: {e}")
                break
    except:
        await msg.reply("❌ Kullanım: /basla 1")

@dp.message_handler(commands=["dur"])
async def dur(msg: types.Message):
    running[msg.from_user.id] = False
    await msg.reply("⛔ Durduruldu.")

# --- ÇALIŞTIRMA ---
if __name__ == "__main__":
    # Flask'ı arka planda başlat
    threading.Thread(target=run_flask, daemon=True).start()
    # Botu ana döngüde başlat
    executor.start_polling(dp, skip_updates=True)
