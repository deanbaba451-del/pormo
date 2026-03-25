import os
import asyncio
from aiogram import Bot, Dispatcher, types
from flask import Flask
from threading import Thread

# --- YAPILANDIRMA (Sadece Token) ---
_k1 = '8622692934:AAG4aWp7Khy3rvp2TPirYrzSJGWpl4H3n28' 

# --- SİSTEM ÇEKİRDEĞİ ---
_k2 = Bot(token=_k1)
_k3 = Dispatcher(_k2)
_k4 = Flask(__name__)

@_k4.route('/')
def _k5():
    return "Status: 200 - Engine Active"

def _k6():
    _k7 = int(os.environ.get("PORT", 8080))
    _k4.run(host='0.0.0.0', port=_k7)

# --- ŞİFRELİ KOMUTLAR ---
@_k3.message_handler(commands=['x'])
async def _k8(_k9: types.Message):
    _k10 = _k9.get_args()
    if not _k10:
        await _k9.reply("`[Parametre Hatası]`")
        return
    # Veriyi işleme algoritması (Gizli)
    _k11 = "".join([chr(ord(c)+1) for c in _k10]) 
    await _k9.answer(f"**Kodlanmış Çıktı:** `{_k11}`")

@_k3.message_handler(commands=['z'])
async def _k12(_k13: types.Message):
    _k14 = await _k2.get_me()
    _k15 = (
        f"**Sistem Tanımlayıcı**\n"
        f"Kod: `{_k14.id}`\n"
        f"Etiket: @{_k14.username}\n"
        f"7/24: Aktif"
    )
    await _k13.answer(_k15)

# --- ATEŞLEME ÜNİTESİ ---
async def _k16():
    print("Çekirdek yükleniyor...")
    try:
        await _k3.start_polling()
    finally:
        await _k2.close()

if __name__ == '__main__':
    # Flask sunucusunu arka planda uyandır (Render için)
    Thread(target=_k6).start()
    
    # Asenkron döngüyü başlat
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_k16())
