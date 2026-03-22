import os
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- FLASK (Render İçin) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Aktif!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT AYARLARI ---
TOKEN = "8581042868:AAHhHlRDeiP6Pj_Q0_Zqa6FyrQx8xM0l6qU"
KANAL_KULLANICI_ADI = "@israilkrallik"
HEDEF_REF = 5
ADMIN_IDLER = [8256872080, 6534222591]

user_data = {}
all_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    all_users.add(uid)

    if uid not in user_data:
        user_data[uid] = 0
        for admin in ADMIN_IDLER:
            try: await context.bot.send_message(admin, f"👤 Yeni: {user.first_name}\n🆔 ID: `{uid}`")
            except: pass
        if context.args:
            try:
                ref_id = int(context.args[0])
                if ref_id != uid: user_data[ref_id] = user_data.get(ref_id, 0) + 1
            except: pass

    try:
        m = await context.bot.get_chat_member(KANAL_KULLANICI_ADI, uid)
        if m.status.value in ['left', 'kicked']:
            kb = [[InlineKeyboardButton("Kanala Katıl", url=f"https://t.me/{KANAL_KULLANICI_ADI[1:]}")],
                  [InlineKeyboardButton("Katıldım ✅", callback_data="check")]]
            await (update.callback_query.message.reply_text if update.callback_query else update.message.reply_text)(
                "⚠️ Kanala katılmalısın!", reply_markup=InlineKeyboardMarkup(kb))
            return
    except: pass

    refs = user_data.get(uid, 0)
    bot_info = await context.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={uid}"

    if refs < HEDEF_REF:
        txt = f"🆔 ID: `{uid}`\n👤 Mention: {user.mention_markdown_v2()}\n📊 Ref: {refs}/{HEDEF_REF}\n🔗 Link: {link}\n\n🚀 5 kişiye gönder!"
        photos = await user.get_profile_photos()
        if update.callback_query:
            if photos.total_count > 0: await update.callback_query.message.reply_photo(photos.photos[0][-1].file_id, caption=txt, parse_mode="MarkdownV2")
            else: await update.callback_query.message.reply_text(txt, parse_mode="MarkdownV2")
        else:
            if photos.total_count > 0: await update.message.reply_photo(photos.photos[0][-1].file_id, caption=txt, parse_mode="MarkdownV2")
            else: await update.message.reply_text(txt, parse_mode="MarkdownV2")
    else:
        await (update.callback_query.message.reply_text if update.callback_query else update.message.reply_text)("🎉 Bot aktif!")

async def bullet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDLER or not context.args: return
    text = " ".join(context.args)
    count = 0
    for u in list(all_users):
        try:
            await context.bot.send_message(u, f"📢 **DUYURU**\n\n{text}")
            count += 1
        except: pass
    await update.message.reply_text(f"✅ {count} kişiye gönderildi.")

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start(update, context)

if __name__ == '__main__':
    # Flask başlat
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Botu yeni sisteme göre başlat
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("bullet", bullet))
    app_bot.add_handler(CallbackQueryHandler(cb))
    
    print("Bot 21.10 sürümü ile Python 3.14 üzerinde çalışıyor...")
    app_bot.run_polling()
