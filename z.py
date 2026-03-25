import asyncio
import re
import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
import google.generativeai as genai

app = Flask('')
@app.route('/')
def home():
    return "bot aktif"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

telegram_token = "8426909483:AAEm793CMn4kt-FOT9OCaLIxaD1T2EyekXI"
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
        await message.answer(temiz_cevap)
    except Exception:
        pass

async def main():
    print("hasretsex")
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
