import os
import random
import asyncio
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- AYARLAR ---
TOKEN = "8529963153:AAFYrV9um5JbsYz24_0uO1tg3YDrfnglCtE"
ADMIN_ID = 6534222591

db = {} # Kullanıcı verileri

# --- RENDER HEALTH CHECK ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- YARDIMCI FONKSİYONLAR ---
def get_user(uid, name):
    if uid not in db:
        db[uid] = {"boy": 10, "hak": 2, "last_reset": datetime.now(), "name": name}
    return db[uid]

async def check_group(update: Update):
    if update.effective_chat.type == "private":
        await update.message.reply_text("🚫 Bu komut sadece *gruplarda* çalışır!", parse_mode="Markdown")
        return False
    return True

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🍆 ALEM HASTAYA HOŞ GELDİN ASLAN PARÇASI! 🍆\n\n"
        "Burası korkakların değil, devasa malı olanların er meydanı! 🚀\n\n"
        "🔥 KOMUTLAR:\n"
        "📏 /uzat | 🏆 /siralama | 🪙 /yt\n"
        "🎰 /slot | 🃏 /bk | ⚔️ /vs\n\n"
        "🚀 Hadi, beni gruba at ve kaosu başlat!\n"
        "⚡ @komtanim"
    )
    await update.message.reply_text(msg)

# --- BUL KARAYI (BK) MANTIĞI ---
async def bk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_group(update): return
    uid = update.effective_user.id
    name = update.effective_user.first_name
    user = get_user(uid, name)

    try:
        miktar_str = context.args[0]
        miktar = user["boy"] if miktar_str == "all" else int(miktar_str)
    except:
        await update.message.reply_text("❗ Kullanım: /bk <miktar> veya /bk all\n(Bul Karayı Al Parayı: 1/3 Şans, x3 Kazanç!)")
        return

    if miktar <= 0 or miktar > user["boy"]:
        await update.message.reply_text(f"❗ Yetersiz boy! Senin malın: {user['boy']} cm")
        return

    keyboard = [
        [InlineKeyboardButton("🥤 1", callback_data=f"bk_1_{miktar}_{uid}"),
         InlineKeyboardButton("🥤 2", callback_data=f"bk_2_{miktar}_{uid}"),
         InlineKeyboardButton("🥤 3", callback_data=f"bk_3_{miktar}_{uid}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    sent_msg = await update.message.reply_text(
        f"🃏 **BUL KARAYI AL PARAYI!** 🃏\n👤 {name}\n🍆 Bahis: {miktar} cm\n❓ Kara (🃏) hangi bardağın altında?",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

    # 20 Saniye Zaman Aşımı
    context.job_queue.run_once(bk_timeout, 20, data={"chat_id": update.effective_chat.id, "user_id": uid, "name": name, "msg_id": sent_msg.message_id})

async def bk_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")
    secim = int(data[1])
    miktar = int(data[2])
    owner_id = int(data[3])

    if query.from_user.id != owner_id:
        await query.answer("Bu senin bahsin değil! ✋", show_alert=True)
        return

    await query.answer()
    user = db[owner_id]
    kara_nerede = random.randint(1, 3)
    
    # Bardakları görselleştirme
    bardaklar = ["🥤", "🥤", "🥤"]
    bardaklar[secim-1] = "🚫" if secim != kara_nerede else "🃏"
    bardaklar[kara_nerede-1] = "🃏"
    visual = f"| {' | '.join(bardaklar)} |"

    if secim == kara_nerede:
        kazanc = miktar * 2 # Toplamda 3 katı olması için +2 ekliyoruz
        user["boy"] += kazanc
        txt = f"✅ **KAZANDIN!** ✅\n{visual}\n\nDoğru tahmin! Kara {kara_nerede}. bardaktaydı.\n📈 Ödül: +{kazanc} cm\n📏 Yeni Boy: {user['boy']} cm 🚀"
    else:
        user["boy"] -= miktar
        txt = f"❌ **YANLIŞ BARDAK!** ❌\n{visual}\n\nSen {secim}. bardağı seçtin ama Kara {kara_nerede}. bardaktaydı!\n📉 Giden: -{miktar} cm\n📏 Yeni Boy: {user['boy']} cm 🥀\n\n💬 💩 Bu ne eziklik? Kaybedenler kulübü başkanı seçildin!"

    await query.edit_message_text(txt, parse_mode="Markdown")

async def bk_timeout(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        await context.bot.edit_message_text(
            chat_id=job.data["chat_id"],
            message_id=job.data["msg_id"],
            text=f"⚠️ **{job.data['name']}**, 20 saniye içinde elini cebinden çıkarıp seçim yapmadığın için bahis iptal! 💤",
            parse_mode="Markdown"
        )
    except: pass

# --- DİĞER KOMUTLAR (SLOT, UZAT VB. TEMEL MANTIK) ---
async def uzat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_group(update): return
    user = get_user(update.effective_user.id, update.effective_user.first_name)
    if user["hak"] <= 0:
        await update.message.reply_text("⏳ Sakin ol şampiyon, motoru yakacaksın. Hakların bitti.")
        return
    artis = random.randint(1, 5)
    user["boy"] += artis
    user["hak"] -= 1
    await update.message.reply_text(f"🔥 **HELAL OLSUN!** 🔥\n🍆 Penisini tam {artis} cm uzattın!\n📏 Yeni boyun: {user['boy']} cm")

# --- ANA ÇALIŞTIRICI ---
def main():
    threading.Thread(target=run_health_check, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("uzat", uzat))
    app.add_handler(CommandHandler("bk", bk))
    app.add_handler(CallbackQueryHandler(bk_callback, pattern="^bk_"))
    
    print("Bot başlatıldı...")
    app.run_polling()

if __name__ == '__main__':
    main()
