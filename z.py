import os
import asyncio
import uuid
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC, error

app = Flask('')

@app.route('/')
def home():
    return "bot aktif"

def run_web():
    app.run(host='0.0.0.0', port=8080)

NAME, ARTIST, PHOTO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("send audio file (mp3, m4a, wav, ogg)")
    return NAME

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_data = update.message.audio or update.message.voice or update.message.document
    
    if not audio_data:
        return NAME

    unique_id = str(uuid.uuid4())
    ext = ".mp3" 
    if hasattr(audio_data, 'file_name') and audio_data.file_name:
        ext = os.path.splitext(audio_data.file_name)[1].lower()
    
    path = f"{unique_id}{ext}"
    
    try:
        file = await audio_data.get_file()
        await file.download_to_drive(path)
        
        context.user_data['file_path'] = path
        context.user_data['extension'] = ext
        context.user_data['unique_id'] = unique_id
        
        await update.message.reply_text("send new song name")
        return NAME
    except Exception:
        if os.path.exists(path): os.remove(path)
        return ConversationHandler.END

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['song_name'] = update.message.text
    await update.message.reply_text("send new artist name")
    return ARTIST

async def handle_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['artist_name'] = update.message.text
    await update.message.reply_text("send cover photo or /skip")
    return PHOTO

async def process_tags(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_path=None):
    path = context.user_data.get('file_path')
    ext = context.user_data.get('extension', '.mp3')
    song_name = context.user_data.get('song_name', 'Unknown')
    artist_name = context.user_data.get('artist_name', 'Unknown')

    if not path or not os.path.exists(path):
        return ConversationHandler.END

    await update.message.reply_text("processing...")

    try:
        if ext == '.mp3':
            try:
                audio = MP3(path, ID3=ID3)
                if audio.tags is None: audio.add_tags()
                else: audio.tags.delall('APIC')
            except Exception:
                audio = MP3(path, ID3=ID3)
                audio.add_tags()

            audio.tags.add(TIT2(encoding=3, text=song_name))
            audio.tags.add(TPE1(encoding=3, text=artist_name))
            
            if photo_path and os.path.exists(photo_path):
                with open(photo_path, 'rb') as img:
                    audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img.read()))
            audio.save(v2_version=3)
        
        else:
            # MP3 dışındaki formatlar (m4a, ogg, wav)
            audio = mutagen.File(path)
            if audio is not None:
                if ext == '.m4a':
                    audio['\xa9nam'] = [song_name]
                    audio['\xa9ART'] = [artist_name]
                else:
                    audio['title'] = [song_name]
                    audio['artist'] = [artist_name]
                audio.save()

        with open(path, 'rb') as final_audio:
            await update.message.reply_audio(audio=final_audio, title=song_name, performer=artist_name)
        
        await update.message.reply_text("done. /start for new")

    except Exception:
        pass
    finally:
        if path and os.path.exists(path): os.remove(path)
        if photo_path and os.path.exists(photo_path): os.remove(photo_path)
        context.user_data.clear()

    return ConversationHandler.END

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        unique_id = context.user_data.get('unique_id')
        photo = await update.message.photo[-1].get_file()
        photo_path = f"{unique_id}.jpg"
        await photo.download_to_drive(photo_path)
        return await process_tags(update, context, photo_path)
    except Exception:
        return await process_tags(update, context)

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_tags(update, context)

if __name__ == '__main__':
    Thread(target=run_web).start()
    
    token = "8591388747:AAEPbKMA3xf7krk-4p0syaab7iMvSB19H6k"
    app_bot = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.AUDIO | filters.Document.AUDIO | filters.VOICE, handle_audio)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_artist)],
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo), CommandHandler('skip', skip_photo)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    app_bot.add_handler(conv_handler)
    app_bot.add_handler(CommandHandler('start', start))
    app_bot.run_polling()

