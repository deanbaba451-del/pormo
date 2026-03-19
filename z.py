import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- AYARLAR ---
api_id = 20275001
api_hash = "26e474f4a17fe5b306cc6ecfd2a1ed55"
string_session = "1BJWap1w... (Buraya session stringini koy)" # Güvenliğin için bunu gizli tut!
owners = [6534222591] 

# Client başlatma
client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    # Sadece sahiplerden gelen mesajları kontrol etme veya muaf tutma mantığı
    if event.sender_id in owners:
        return

    try:
        # Mesajı silme işlemi
        await event.delete()
    except Exception as e:
        print(f"Hata oluştu: {e}")

async def main():
    # Botu başlat
    await client.start()
    print("Bot aktif ve çalışıyor...")
    
    # Render gibi platformlarda bağlantının kopmaması için süresiz bekleme
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
