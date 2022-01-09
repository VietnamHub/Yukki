from pyrogram import Client, filters
from pyrogram.types import Message

from Yukki import SUDOERS, app
from Yukki.Database import blacklist_chat, blacklisted_chats, whitelist_chat

__MODULE__ = "Danh sách đen"
__HELP__ = """


/blacklistedchat 
- Kiểm tra các cuộc trò chuyện trong danh sách đen của Bot.


**Note:**
Chỉ dành cho người dùng Sudo.


/blacklistchat [CHAT_ID] 
- Đưa mọi cuộc trò chuyện vào danh sách cấm sử dụng Music Bot


/whitelistchat [CHAT_ID] 
- Đưa mọi cuộc trò chuyện vào danh sách đen không được sử dụng Music Bot

"""


@app.on_message(filters.command("blacklistchat") & filters.user(SUDOERS))
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**Usage:**\n/blacklistchat [CHAT_ID]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text("Trò chuyện đã được đưa vào danh sách đen.")
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text(
            "Nhóm đã được đưa vào danh sách đen thành công"
        )
    await message.reply_text("Đã xảy ra lỗi, hãy kiểm tra nhật ký.")


@app.on_message(filters.command("whitelistchat") & filters.user(SUDOERS))
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**Usage:**\n/whitelistchat [CHAT_ID]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text("Trò chuyện đã được đưa vào danh sách trắng.")
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(
            "Nhóm đã được đưa vào danh sách trắng thành công"
        )
    await message.reply_text("Đã xảy ra lỗi, hãy kiểm tra nhật ký.")


@app.on_message(filters.command("blacklistedchat"))
async def blacklisted_chats_func(_, message: Message):
    text = "**Trò chuyện trong danh sách đen:**\n\n"
    j = 0
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "Private"
        j = 1
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    if j == 0:
        await message.reply_text("Không có cuộc trò chuyện trong danh sách đen")
    else:
        await message.reply_text(text)
