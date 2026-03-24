import os
import asyncio
from flask import Flask
from telethon import TelegramClient, events, functions, types, utils
from telethon.sessions import StringSession, MemorySession
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError, PeerFloodError

# --- yapılandırma ---
API_ID = 38517910
API_HASH = "974a2b5877fab4867b1b48276d9e1c39"
BOT_TOKEN = "8503702390:AAH2ZVUKn0v4v3EbnSYSM0KaVZM_FxNf5ec"

app = Flask(__name__)

@app.route('/')
def home(): return "bot aktif"

bot = TelegramClient(MemorySession(), API_ID, API_HASH)
user_states = {}

async def start_bot():
    await bot.start(bot_token=BOT_TOKEN)
    print("--- bot hazir ---")

@bot.on(events.NewMessage)
async def handler(event):
    msg = event.text.lower() if event.text else ""
    user_id = event.sender_id
    state = user_states.get(user_id)

    if msg == "/start" or msg == "start":
        await event.reply("selam, aktarim baslatmak icin numaranı yaz (orn: +905xxx):")
        user_states[user_id] = {'step': 'phone'}
        return

    # 1. ADIM: NUMARA
    if state and state['step'] == 'phone':
        client = TelegramClient(MemorySession(), API_ID, API_HASH)
        await client.connect()
        try:
            send_code = await client.send_code_request(event.text)
            user_states[user_id] = {'step': 'code', 'client': client, 'phone': event.text, 'hash': send_code.phone_code_hash}
            await event.reply("kodu yaz:")
        except Exception as e:
            await event.reply(f"hata: {str(e).lower()}")
        return

    # 2. ADIM: KOD VE LISTE
    if state and state['step'] == 'code':
        try:
            client = state['client']
            await client.sign_in(state['phone'], event.text, phone_code_hash=state['hash'])
            dialogs = []
            text = "giris yapildi. kaynak grubu sec:\n\n"
            i = 1
            async for d in client.iter_dialogs():
                if d.is_group or d.is_channel:
                    dialogs.append(d)
                    text += f"{i}. {d.name}\n"
                    i += 1
            user_states[user_id].update({'step': 'source', 'dialogs': dialogs})
            await event.reply(text)
        except Exception as e:
            await event.reply(f"hata: {str(e).lower()}")
        return

    # 3. ADIM: KAYNAK SECIMI
    if state and state['step'] == 'source':
        try:
            idx = int(event.text) - 1
            source = state['dialogs'][idx]
            user_states[user_id].update({'step': 'target', 'source_id': source.id})
            await event.reply(f"kaynak: {source.name}\nsimdi hedef grubu sec:")
        except:
            await event.reply("listeden numara sec.")
        return

    # 4. ADIM: HEDEF SECIMI VE SAYI ISTEME
    if state and state['step'] == 'target':
        try:
            idx = int(event.text) - 1
            target = state['dialogs'][idx]
            user_states[user_id].update({'step': 'limit', 'target_id': target.id})
            await event.reply(f"hedef: {target.name}\nkac uye eklensin? (sayi yazin):")
        except:
            await event.reply("listeden numara sec.")
        return

    # 5. ADIM: SAYI ALMA VE FILTRELI AKTARIM
    if state and state['step'] == 'limit':
        try:
            limit_val = int(event.text)
            source_id = state['source_id']
            target_id = state['target_id']
            client = state['client']
            
            await event.reply(f"kontrol yapiliyor ve {limit_val} kisi icin islem basliyor...")
            
            # Hedef gruptaki mevcut uyeleri cek (mukerrer onlemek icin)
            target_members = await client.get_participants(target_id)
            target_ids = {u.id for u in target_members}
            
            # Kaynak uyeleri cek
            participants = await client.get_participants(source_id, limit=limit_val + 50) # Biraz fazla cekiyoruz filtreleme icin
            
            count = 0
            for u in participants:
                if count >= limit_val: break
                if u.bot or u.deleted or u.id in target_ids:
                    continue
                
                # Etiketleme mantigi: @username yoksa Isim (Mention)
                if u.username:
                    u_label = f"@{u.username}"
                else:
                    first_name = u.first_name or "Kullanıcı"
                    u_label = f"[{first_name}](tg://user?id={u.id})"

                try:
                    await client(functions.channels.InviteToChannelRequest(target_id, [u]))
                    log = f"eklendi: {u_label}"
                    print(log)
                    await bot.send_message(user_id, log, parse_mode='markdown')
                    count += 1
                    await asyncio.sleep(15) 
                
                except UserPrivacyRestrictedError:
                    await bot.send_message(user_id, f"gizlilik engeli: {u_label}", parse_mode='markdown')
                except PeerFloodError:
                    await bot.send_message(user_id, "limit doldu: hesap isleme kapandi.")
                    break
                except FloodWaitError as e:
                    await bot.send_message(user_id, f"bekleme: {e.seconds} saniye...")
                    await asyncio.sleep(e.seconds)
                except Exception:
                    continue
            
            await event.reply(f"islem bitti. toplam {count} yeni kisi eklendi.")
            user_states.pop(user_id)
        except ValueError:
            await event.reply("lutfen sadece rakam girin.")
        except Exception as e:
            await event.reply(f"hata: {str(e).lower()}")
        return

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    loop.create_task(bot.run_until_disconnected())
    try:
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    except:
        loop.run_forever()
