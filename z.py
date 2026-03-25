import asyncio
import re
import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
import google.generativeai as genai

app = Flask('')

@app.route('/')
def home():
    return "hasret ve rei seks yapiyor"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

telegram_token = "8426909483:AAE7HthK3JffdXF_lENjj0qxCD9mOJeXmCU"
gemini_api_key = "AIzaSyAUyCjmXDUxABE8HzU6_faM7FLEilLrgqU"

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = Bot(token=telegram_token)
dp = Dispatcher()

@dp.message()
async def gpt_cevap(message: types.Message):
    try:
        if not message.text: return
        response = model.generate_content(message.text)
        cevap = response.text.lower()
        temiz_cevap = re.sub(r'[^\w\s.,?!]', '', cevap)
        if not temiz_cevap.strip():
            temiz_cevap = "anlasilmadi"
        await message.answer(temiz_cevap)
    except Exception:
        pass

async def main():
    print("hasretsex")
    Thread(target=run, daemon=True).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
