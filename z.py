import asyncio
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, executor
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.channels import InviteToChannelRequest

# --- FLASK AYARLARI (Render Port Hatasını Çözmek İçin) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render PORT değişkenini otomatik atar, yoksa 10000 kullanır
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT AYARLARI ---
BOT_TOKEN = "8730162607:AAF65-aKIv1sd7AmrLSVechf3Z0fT2dMExo"
OWNER_ID = 8256872080

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

allowed_users = {OWNER_ID}
sessions = {}
running = {}
login_data = {}

GROUP = "grup_username"
users = ["kullanici1", "kullanici2"]

def is_allowed(uid):
    return uid in allowed_users

# --- BOT KOMUTLARI ---

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if not is_allowed(msg.from_user.id): return
    await msg.reply("📱 Telefon numaranı gönder (+905xx...)")

@dp.message_handler(commands=["yetki"])
async def yetki(msg: types.Message):
    if msg.from_user.id != OWNER_ID: return
    try:
        _, act, uid = msg.text.split()
        uid = int(uid)
        if act == "ekle": allowed_users.add(uid)
        elif act == "sil": allowed_users.discard(uid)
        await msg.reply(f"✅ İşlem tamam: {uid}")
    except:
        await msg.reply("/yetki ekle 12345")

@dp.message_handler(lambda m: m.text.startswith("+"))
async def phone(msg: types.Message):
    if not is_allowed(msg.from_user.id): return
    login_data[msg.from_user.id] = {"phone": msg.text}
    await msg.reply("API ID gönder")

@dp.message_handler(lambda m: m.text.isdigit() and len(m.text) < 10)
async def api_id(msg: types.Message):
    if not is_allowed(msg.from_user.id): return
    login_data[msg.from_user.id]["api_id"] = int(msg.text)
    await msg.reply("API HASH gönder")

@dp.message_handler(lambda m: len(m.text) > 20)
async def api_hash(msg: types.Message):
    uid = msg.from_user.id
    if not is_allowed(uid): return
    data = login_data[uid]
    data["api_hash"] = msg.text
    
    client = TelegramClient(f"session_{uid}", data["api_id"], data["api_hash"])
    await client.connect()
    sent_code = await client.send_code_request(data["phone"])
    data["hash"] = sent_code.phone_code_hash
    sessions[uid] = client
    await msg.reply("📩 Kod gönderildi, buraya yaz:")

@dp.message_handler(lambda m: m.text.isdigit() and len(m.text) == 5)
async def code(msg: types.Message):
    uid = msg.from_user.id
    client = sessions[uid]
    data = login_data[uid]
    try:
        await client.sign_in(data["phone"], msg.text, phone_code_hash=data["hash"])
        await msg.reply("✅ Giriş OK!\n/basla")
    except SessionPasswordNeededError:
        await msg.reply("🔒 2FA Şifreni gir")

@dp.message_handler(commands=["basla"])
async def basla(msg: types.Message):
    uid = msg.from_user.id
    if not is_allowed(uid) or uid not in sessions: return
    
    client = sessions[uid]
    running[uid] = True
    entity = await client.get_entity(GROUP)
    await msg.reply("🚀 Başlatıldı")

    while running.get(uid):
        try:
            # Invite işlemi (Sınırları aşmamak için süreye dikkat)
            await client(InviteToChannelRequest(entity, users[:3]))
            await asyncio.sleep(60) 
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            break

@dp.message_handler(commands=["dur"])
async def dur(msg: types.Message):
    running[msg.from_user.id] = False
    await msg.reply("⛔ Durduruldu")

# --- ANA ÇALIŞTIRICI ---

if __name__ == "__main__":
    # 1. Flask'ı ayrı bir thread'de başlat (Portu dinlemesi için)
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # 2. Aiogram Botu başlat
    executor.start_polling(dp, skip_updates=True)
