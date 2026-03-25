import os
import json
import uuid
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask

token = '8622692934:AAERQ9C5UjHXA9uN2RLEmlZ-TxILpuEUd98'
bot = Bot(token=token)
dp = Dispatcher(bot)
app = Flask(__name__)
storage = {}

@app.route('/')
def home():
    return "active"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(content_types=['text', 'document'])
async def msg(m: types.Message):
    id = str(uuid.uuid4())[:8]
    val = m.text if m.text else m.document.file_name
    
    user = "bilinmiyor"
    if m.forward_from:
        user = m.forward_from.id
    elif m.forward_sender_name:
        user = m.forward_sender_name

    storage[id] = {"v": val, "u": user}
    
    btn = types.InlineKeyboardMarkup()
    btn.add(
        types.InlineKeyboardButton("dosya", callback_data=f"f_{id}"),
        types.InlineKeyboardButton("link", callback_data=f"l_{id}")
    )
    await m.reply(f"kim demis: {user}\ncevap: {val}\nhazir. secim yap:", reply_markup=btn)

@dp.callback_query_handler(lambda c: c.data)
async def call(c: types.CallbackQuery):
    act, id = c.data.split('_')
    if id not in storage:
        await c.answer("hata: veri yok")
        return

    res = json.dumps({
        "kim": storage[id]["u"],
        "cevabi": storage[id]["v"]
    }, indent=4, ensure_ascii=False)

    if act == 'f':
        path = f"{id}.json"
        with open(path, "w", encoding="utf-8") as f:
            f.write(res)
        await bot.send_document(c.from_user.id, types.InputFile(path))
        if os.path.exists(path): os.remove(path)
    
    elif act == 'l':
        await c.message.edit_text(f"link: hastebin.com/{id}")

    await c.answer()

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
