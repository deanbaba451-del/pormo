import os, random, threading, asyncio
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- RENDER WEB SERVER ---
server = Flask(__name__)
@server.route('/')
def health(): return "Bot 7/24 Aktif!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
TOKEN = "8529963153:AAF_A3WOpcHdBM5_5lhlrU6rqjmKlRniZzs"
ADMIN_ID = 6534222591
db = {} # Bellekte tutulan veriler
authorized_groups = set()

def get_u(uid, name):
    if uid not in db: db[uid] = {"boy": 10, "hak": 2, "last_reset": datetime.now(), "name": name}
    return db[uid]

async def group_only(update: Update):
    if update.effective_chat.type == "private":
        await update.message.reply_text("🚫 Bu komut sadece *gruplarda* çalışır!", parse_mode="Markdown")
        return False
    return True

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🍆 **KRALLIĞA HOŞ GELDİN ASLAN PARÇASI!** 🍆\n\n"
        "Burası korkakların değil, devasa malı olanların er meydanı! 🚀\n\n"
        "🔥 **KOMUTLAR:**\n\n"
        "🍆 **Genel:**\n"
        "📏 /uzat — Malına mal kat! (12 saatte 2 hak)\n"
        "🏆 /siralama — En büyükler listesi!\n"
        "📏 /boyum — Kendi malının durumunu gör!\n"
        "📏 /boyu — Başkasının malına bak!\n\n"
        "🎲 **Kumarhane:**\n"
        "🪙 /yt — Yazı tura ile katla!\n"
        "🎰 /slot — Slot çevir, 4 katını kazan!\n"
        "🃏 /bk — Bul Karayı, 3 katını al!\n"
        "⚔️ /vs — Birine meydan oku!\n\n"
        "🚀 **Etkileşim:**\n"
        "🔥 /kaldir — Birini gaza getir, şaha kaldır!\n"
        "📉 /indir — Birini göm, içine kaçsın!\n\n"
        "🛡️ **Yetkililer İçin:**\n"
        "🔓 /prohere — Gruba yetki ver.\n"
        "🔒 /unprohere — Yetki al.\n\n"
        "🎁 **Promosyon:**\n"
        "📦 /promo <kod> — Promosyon kodu kullan.\n\n"
        "🔐 **Admin:**\n"
        "🎫 /promokodolustur — Rastgele kod oluştur.\n\n"
        "🌟 **EMEĞİ GEÇENLER** 🌟\n"
        "⚡ @komtanim & @sucluluk"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# --- GENEL KOMUTLAR ---
async def uzat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_only(update): return
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    if u["hak"] > 0:
        artis = random.randint(1, 5)
        u["boy"] += artis
        u["hak"] -= 1
        txt = f"🔥 **HELAL OLSUN {u['name']}!** 🔥\n🍆 Penisini tam {artis} cm uzattın!\n📏 Yeni boyun: {u['boy']} cm\n\n"
        txt += f"💡 Hala {u['hak']} hakkın daha var!" if u["hak"] > 0 else "💤 Bu periyotluk bitti, dinlen."
        await update.message.reply_text(txt, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⏳ {u['name']}, bu periyot için 2 hakkını da doldurdun!\nSakin ol şampiyon, motoru yakacaksın. Kalan süre: 6 saat 22 dakika ⏰")

async def siralama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_only(update): return
    sort = sorted(db.items(), key=lambda x: x[1]['boy'], reverse=True)[:10]
    txt = "🏆 **Grup Penis Boyu Sıralaması:** 📊\n\n"
    for i, (uid, d) in enumerate(sort, 1):
        txt += f"{i}️. {d['name']} - {d['boy']} cm\n"
    txt += "\nKimin borusu ne kadar öttü bakalım 😎🍆"
    await update.message.reply_text(txt, parse_mode="Markdown")

async def boyum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    await update.message.reply_text(f"🍆 Hey {u['name']}! Şu anki malın durumu: **{u['boy']} cm** 🔥", parse_mode="Markdown")

# --- KUMARHANE ---
async def yt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_only(update): return
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    try: miktar = int(context.args[0])
    except: return await update.message.reply_text("🪙 Kullanım: /yt <miktar>")
    if miktar > u["boy"]: return await update.message.reply_text(f"❗ Yetersiz boy! Malın: {u['boy']} cm")

    gelen = random.choice(["YAZI", "TURA"])
    if random.choice([True, False]):
        u["boy"] += miktar
        await update.message.reply_text(f"🎉 **KAZANDIN!** 🎉\nGelmesi Gereken: 🟡 {gelen}\n🎁 Ödül: +{miktar*2} cm\n📏 Yeni Boy: {u['boy']} cm 🚀")
    else:
        u["boy"] -= miktar
        await update.message.reply_text(f"💀 **KAYBETTİN!** 💀\nGelen: 🦅 {gelen}\n📉 Giden: -{miktar} cm\n📏 Yeni Boy: {u['boy']} cm\n\nEridi gitti malın, geçmiş olsun bücür! 💀")

async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_only(update): return
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    try: miktar = int(context.args[0])
    except: return await update.message.reply_text("🎰 Kullanım: /slot <miktar> veya /slot all")
    if miktar > u["boy"]: return await update.message.reply_text(f"❗ O kadar malın yok! (Senin: {u['boy']} cm)")

    emojis = ["💎", "7️⃣", "🍇", "🍋"]
    res = [random.choice(emojis) for _ in range(3)]
    res_str = f"| {' | '.join(res)} |"
    
    if len(set(res)) == 1:
        win = miktar * 3
        u["boy"] += win
        await update.message.reply_text(f"🎰 **SLOT SONUCU** 🎰\n👉 {res_str} 👈\n\n🔔 Durum: **KAZANDIN!** 🎰\n📈 Değişim: +{win} cm\n📏 Yeni Boy: {u['boy']} cm")
    else:
        u["boy"] -= miktar
        await update.message.reply_text(f"🎰 **SLOT SONUCU** 🎰\n👉 {res_str} 👈\n\n🔔 Durum: **KAYBETTİN!** 🤡\n📉 Değişim: -{miktar} cm\n📏 Yeni Boy: {u['boy']} cm\n\n🤡 Git kumda oyna aslanım!")

# --- ETKİLEŞİM ---
async def kaldir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_only(update): return
    await update.message.reply_text("🔥 ÖFFF! Şuna bak hele, şaha kalktı! Yer gök inliyor! 🚀🍆")

async def indir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_only(update): return
    await update.message.reply_text("📉 Geçmiş olsun kardeşim... İçine kaçtı, büyüteçle arıyoruz. 🔎")

# --- YETKİ VE ADMIN ---
async def prohere(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_only(update): return
    authorized_groups.add(update.effective_chat.id)
    await update.message.reply_text("🔓 **Gruba yetki verildi!** Artık burada kaos serbest.")

async def promokodolustur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Bu komutu sadece global adminler kullanabilir!")
        return
    await update.message.reply_text("🎫 Rastgele promosyon kodu oluşturuldu: **ALEM-FREE-2024**")

# --- ANA ÇALIŞTIRICI ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    handlers = [
        CommandHandler("start", start), CommandHandler("uzat", uzat),
        CommandHandler("siralama", siralama), CommandHandler("boyum", boyum),
        CommandHandler("yt", yt), CommandHandler("slot", slot),
        CommandHandler("kaldir", kaldir), CommandHandler("indir", indir),
        CommandHandler("prohere", prohere), CommandHandler("promokodolustur", promokodolustur)
    ]
    for h in handlers: app.add_handler(h)
    
    print("Penis Can Bot 7/24 Aktif!")
    app.run_polling()

if __name__ == '__main__': main()
