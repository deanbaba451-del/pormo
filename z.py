import os, random, threading, string
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- RENDER PORT SUNUCUSU ---
server = Flask(__name__)
@server.route('/')
def health(): return "Krallık Aktif!", 200
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
TOKEN = "8529963153:AAFon3DWR_GIQ8ezqE7xzMDEOkGg9iGSMTE"
ADMIN_ID = 6534222591
db = {} # {uid: {boy, hak, last_reset, name}}
promos = {} # {kod: miktar}
authorized_groups = set()

def get_u(uid, name):
    if uid not in db:
        db[uid] = {"boy": 10, "hak": 2, "last_reset": datetime.now(), "name": name}
    return db[uid]

async def group_check(update: Update):
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

# --- OYUNLAR VE ETKİLEŞİM ---
async def uzat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_check(update): return
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    if u["hak"] > 0:
        artis = random.randint(1, 6)
        u["boy"] += artis
        u["hak"] -= 1
        await update.message.reply_text(f"🔥 **HELAL OLSUN!**\n🍆 +{artis} cm uzattın!\n📏 Yeni boy: {u['boy']} cm\n💡 Kalan Hak: {u['hak']}")
    else:
        await update.message.reply_text("⏳ Sakin ol şampiyon, motoru yakacaksın! 12 saatte bir 2 hak tazeleyebilirsin.")

async def boyum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    await update.message.reply_text(f"🍆 **{u['name']}**, malın durumu: **{u['boy']} cm** 🔥")

async def boyu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("👀 Bakmak istediğin birini yanıtla!")
    t = update.message.reply_to_message.from_user
    u = get_u(t.id, t.first_name)
    await update.message.reply_text(f"🍆 **{u['name']}** kişisinin malı: **{u['boy']} cm** 👀")

async def siralama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_check(update): return
    sort = sorted(db.items(), key=lambda x: x[1]['boy'], reverse=True)[:10]
    txt = "🏆 **EN BÜYÜKLER LİSTESİ** 🏆\n\n"
    for i, (uid, d) in enumerate(sort, 1):
        txt += f"{i}. {d['name']} — {d['boy']} cm\n"
    await update.message.reply_text(txt)

async def yt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_check(update): return
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    try: mik = int(context.args[0])
    except: return await update.message.reply_text("🪙 Örnek: `/yt 5`")
    if mik > u["boy"]: return await update.message.reply_text("❗ Malın yetersiz!")
    
    kb = [[InlineKeyboardButton("🟡 YAZI", callback_data=f"yt_YAZI_{mik}_{update.effective_user.id}"),
           InlineKeyboardButton("🦅 TURA", callback_data=f"yt_TURA_{mik}_{update.effective_user.id}")]]
    await update.message.reply_text(f"🪙 **YAZI-TURA**\nBahis: {mik} cm", reply_markup=InlineKeyboardMarkup(kb))

async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_check(update): return
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    try: mik = int(context.args[0])
    except: return await update.message.reply_text("🎰 Örnek: `/slot 5`")
    if mik > u["boy"]: return await update.message.reply_text("❗ Malın yetersiz!")
    
    e = ["💎", "7️⃣", "🍇", "🍋"]
    res = [random.choice(e) for _ in range(3)]
    res_s = f"| {' | '.join(res)} |"
    if len(set(res)) == 1:
        u["boy"] += mik * 3
        await update.message.reply_text(f"🎰 **JACKPOT!**\n{res_s}\n✅ +{mik*3} cm kazandın!")
    else:
        u["boy"] -= mik
        await update.message.reply_text(f"🎰 **KAYBETTİN!**\n{res_s}\n📉 -{mik} cm gitti!")

async def bk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await group_check(update): return
    u = get_u(update.effective_user.id, update.effective_user.first_name)
    try: mik = int(context.args[0])
    except: return await update.message.reply_text("🃏 Örnek: `/bk 5`")
    if mik > u["boy"]: return await update.message.reply_text("❗ Malın yetersiz!")

    kb = [[InlineKeyboardButton("🥤 1", callback_data=f"bk_1_{mik}_{update.effective_user.id}"),
           InlineKeyboardButton("🥤 2", callback_data=f"bk_2_{mik}_{update.effective_user.id}"),
           InlineKeyboardButton("🥤 3", callback_data=f"bk_3_{mik}_{update.effective_user.id}")]]
    msg = await update.message.reply_text(f"🃏 **KARA NEREDE?** (3 Kat Kazanç)\nBahis: {mik} cm", reply_markup=InlineKeyboardMarkup(kb))
    context.job_queue.run_once(lambda c: context.bot.edit_message_text("⚠️ Süre bitti!", msg.chat_id, msg.message_id), 20)

async def vs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("⚔️ VS için birini yanıtla!")
    t = update.message.reply_to_message.from_user
    kb = [[InlineKeyboardButton("✅ KABUL ET", callback_data=f"vsacc_{update.effective_user.id}_{t.id}")]]
    await update.message.reply_text(f"⚔️ **{update.effective_user.first_name}**, **{t.first_name}** kişisine meydan okudu!", reply_markup=InlineKeyboardMarkup(kb))

# --- YETKİ VE PROMO ---
async def prohere(update: Update, context: ContextTypes.DEFAULT_TYPE):
    authorized_groups.add(update.effective_chat.id)
    await update.message.reply_text("🔓 **Grup yetkilendirildi.** Artık tüm komutlar aktif!")

async def unprohere(update: Update, context: ContextTypes.DEFAULT_TYPE):
    authorized_groups.discard(update.effective_chat.id)
    await update.message.reply_text("🔒 **Yetki alındı.**")

async def promokodolustur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    promos[kod] = random.randint(10, 50)
    await update.message.reply_text(f"🎫 **Kod:** `{kod}` (+{promos[kod]} cm)")

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    kod = context.args[0]
    if kod in promos:
        u = get_u(update.effective_user.id, update.effective_user.first_name)
        u["boy"] += promos[kod]
        await update.message.reply_text(f"✅ Kod kullanıldı! +{promos[kod]} cm eklendi.")
        del promos[kod]
    else: await update.message.reply_text("❌ Geçersiz kod!")

# --- CALLBACK ---
async def call_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data.split("_")
    u = get_u(q.from_user.id, q.from_user.first_name)

    if d[0] == "yt":
        if q.from_user.id != int(d[3]): return await q.answer("Senin bahsin değil!", show_alert=True)
        res = random.choice(["YAZI", "TURA"])
        mik = int(d[2])
        if d[1] == res: u["boy"] += mik; t = f"✅ **KAZANDIN!**\nGelen: {res}\n📏 Boy: {u['boy']}"
        else: u["boy"] -= mik; t = f"💀 **KAYBETTİN!**\nGelen: {res}\n📏 Boy: {u['boy']}"
        await q.edit_message_text(t)
    elif d[0] == "bk":
        if q.from_user.id != int(d[3]): return await q.answer("Senin bahsin değil!", show_alert=True)
        kara = random.randint(1, 3)
        mik = int(d[2])
        if int(d[1]) == kara: u["boy"] += mik*2; t = f"✅ **BULDUN!** Kara {kara}. bardaktaydı!\n📏 Boy: {u['boy']}"
        else: u["boy"] -= mik; t = f"❌ **YANLIŞ!** Kara {kara}. bardaktaydı!\n📏 Boy: {u['boy']}"
        await q.edit_message_text(t)
    elif d[0] == "vsacc":
        if q.from_user.id != int(d[2]): return await q.answer("Sana söylenmedi!", show_alert=True)
        win = random.choice([get_u(int(d[1]), "P1"), get_u(int(d[2]), "P2")])
        los = get_u(int(d[2]), "P2") if win["boy"] == get_u(int(d[1]), "P1")["boy"] else get_u(int(d[1]), "P1")
        p = random.randint(3, 10); win["boy"] += p; los["boy"] -= p
        await q.edit_message_text(f"⚔️ Kazanan: **{win['name']}** (+{p})\n💀 Kaybeden: **{los['name']}** (-{p})")

# --- MAIN ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    cmds = [
        ("start", start), ("uzat", uzat), ("boyum", boyum), ("boyu", boyu),
        ("siralama", siralama), ("yt", yt), ("slot", slot), ("bk", bk),
        ("vs", vs), ("prohere", prohere), ("unprohere", unprohere),
        ("promokodolustur", promokodolustur), ("promo", promo),
        ("kaldir", lambda u, c: u.message.reply_text("🔥 ŞAHA KALKTI! 🚀🍆")),
        ("indir", lambda u, c: u.message.reply_text("📉 İçine kaçtı... 🔎"))
    ]
    for c, f in cmds: app.add_handler(CommandHandler(c, f))
    app.add_handler(CallbackQueryHandler(call_back))
    
    app.run_polling()

if __name__ == '__main__': main()
