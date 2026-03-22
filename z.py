import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- AYARLAR ---
TOKEN = "8581042868:AAHhHlRDeiP6Pj_Q0_Zqa6FyrQx8xM0l6qU"
KANAL_KULLANICI_ADI = "@israilkrallik"
HEDEF_REF = 5
ADMIN_IDLER = [8256872080, 6534222591] # Bildirim gidecek ve duyuru yapacak kişiler

user_data = {} # Referansları tutar
all_users = set() # Duyuru için tüm kullanıcıları tutar

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Callback veya normal mesaj kontrolü
    user = update.effective_user
    uid = user.id
    all_users.add(uid)

    # 1. REFERANS KAYDI
    if uid not in user_data:
        user_data[uid] = 0
        # Adminlere bildirim gönder
        for admin in ADMIN_IDLER:
            try:
                await context.bot.send_message(admin, f"👤 Yeni kullanıcı: {user.first_name}\n🆔 ID: `{uid}`\n🏷 @{user.username}")
            except: pass
            
        if context.args:
            try:
                ref_id = int(context.args[0])
                if ref_id != uid:
                    user_data[ref_id] = user_data.get(ref_id, 0) + 1
            except: pass

    # 2. KANAL KONTROLÜ
    try:
        m = await context.bot.get_chat_member(KANAL_KULLANICI_ADI, uid)
        if m.status in ['left', 'kicked']:
            kb = [[InlineKeyboardButton("Kanala Katıl", url=f"https://t.me/{KANAL_KULLANICI_ADI[1:]}")],
                  [InlineKeyboardButton("Katıldım ✅", callback_data="check")]]
            text = "⚠️ **DUR!**\n\nBotu kullanabilmek için kanala katılmalısın."
            if update.callback_query:
                await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
            else:
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
            return
    except:
        return

    # 3. REF DURUMU VE PROFİL
    refs = user_data.get(uid, 0)
    bot_info = await context.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={uid}"

    if refs < HEDEF_REF:
        # Görseldeki gibi şık metin
        txt = (
            f"🆔 **ID:** `{uid}`\n"
            f"👤 **Mention:** {user.mention_markdown()}\n"
            f"🏷 **Kullanıcı:** @{user.username if user.username else 'Yok'}\n\n"
            f"📊 **Ref:** {refs}/{HEDEF_REF}\n"
            f"🔗 **Link:** {link}\n\n"
            f"🚀 Botu aktif etmek için linkini 5 kişiyle paylaş!"
        )
        
        try:
            photos = await user.get_profile_photos()
            if photos.total_count > 0:
                photo_id = photos.photos[0][-1].file_id
                if update.callback_query:
                    await update.callback_query.message.reply_photo(photo_id, caption=txt, parse_mode="Markdown")
                else:
                    await update.message.reply_photo(photo_id, caption=txt, parse_mode="Markdown")
            else:
                if update.callback_query:
                    await update.callback_query.message.reply_text(txt, parse_mode="Markdown")
                else:
                    await update.message.reply_text(txt, parse_mode="Markdown")
        except:
            pass
    else:
        msg = "🎉 **Tebrikler!** 5 referansa ulaştın. Bot artık senin için aktif!"
        if update.callback_query: await update.callback_query.message.reply_text(msg, parse_mode="Markdown")
        else: await update.message.reply_text(msg, parse_mode="Markdown")

# 4. DUYURU SİSTEMİ (/bullet mesaj)
async def bullet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDLER:
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: `/bullet Mesajınız`", parse_mode="Markdown")
        return

    duyuru_metni = " ".join(context.args)
    basarili = 0
    
    for user_id in all_users:
        try:
            await context.bot.send_message(user_id, f"📢 **YENİ DUYURU**\n\n{duyuru_metni}", parse_mode="Markdown")
            basarili += 1
        except: pass
    
    await update.message.reply_text(f"✅ Duyuru {basarili} kişiye gönderildi.")

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    try: await update.callback_query.message.delete()
    except: pass
    await start(update, context)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bullet", bullet))
    app.add_handler(CallbackQueryHandler(cb))
    
    print("Bot Render/IDE üzerinde başlatıldı...")
    app.run_polling()
