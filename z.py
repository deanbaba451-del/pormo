api_id = 20275001
api_hash = "26e474f4a17fe5b306cc6ecfd2a1ed55"
string_session = "1BJWap1wBu6BWmzbKhuKET-vgh7kHrYnmrAFbQzQHw6DZaHu_61YMZCiB_DJakE5TVHGuxEasypULtDEMBan-VnxS105s04bMvdgVjYz6XW65Jk2njBCe1xdZbVb3Mikrkcao4MgyGuWtNEvJPQoLl9X3m7jw4EtJoNQ16_ovggEhvgPqZyWbEym2gJ9U7m3zJgu5CmviSLAUKPIHvb2Dreu1QFrK1__SBZiNXGz-RU3tGcgxLSLre_EyFq7Px-4BNVY9qgwrJnpdet7_OqzGXLW4EHBow5IkhAZgxGltFOHsvSDKYNfT_LYJXlA06emAxNwGGz9q72GJ3XEQWZLOmi62KdASAbI="
owners = [6534222591]

user_bot = Client("my_account", api_id=api_id, api_hash=api_hash, session_string=string_session)

active_chats = set()

@user_bot.on_message(filters.user(owners) & filters.command("b", prefixes="."))
async def start_nuke(client, message):
    active_chats.add(message.chat.id)
    await message.edit_text("online")

@user_bot.on_message(filters.user(owners) & filters.command("i", prefixes="."))
async def stop_nuke(client, message):
    if message.chat.id in active_chats:
        active_chats.remove(message.chat.id)
    await message.edit_text("offline")

@user_bot.on_message(filters.group, group=1)
async def cleaner(client, message):
    if message.chat.id in active_chats:
        if message.from_user and message.from_user.id in owners:
            return
        try:
            await message.delete()
        except:
            pass

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    user_bot.run()    keep_alive()
    user_bot.run()
