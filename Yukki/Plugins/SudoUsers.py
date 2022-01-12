import asyncio
import os
import shutil
import subprocess
from sys import version as pyver

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import LOG_SESSION, OWNER_ID
from Yukki import BOT_ID, BOT_USERNAME, MUSIC_BOT_NAME, OWNER_ID, SUDOERS, app
from Yukki.Database import (add_gban_user, add_off, add_on, add_sudo,
                            get_active_chats, get_served_chats, get_sudoers,
                            is_gbanned_user, remove_active_chat,
                            remove_gban_user, remove_served_chat, remove_sudo,
                            set_video_limit)

__MODULE__ = "Nhà phát triển"
__HELP__ = """


/sudolist 
    Kiểm tra danh sách người dùng sudo của Bot.


**Note:**
Chỉ dành cho người dùng Sudo.

/addsudo [Username or Reply to a user]
- Để thêm người dùng trong số người dùng Sudo của Bot.

/delsudo [Username or Reply to a user]
- Để xóa một người dùng khỏi người dùng Sudo của Bot.

/restart 
- Khởi động lại Bot [Tất cả tải xuống, bộ nhớ cache, tệp thô cũng sẽ bị xóa].

/maintenance [enable / disable]
- Khi được kích hoạt, Bot sẽ ở chế độ bảo trì. Không ai có thể chơi Nhạc bây giờ!

/logger [enable / disable]
- Khi được bật Bot sẽ ghi lại các truy vấn được tìm kiếm trong nhóm trình ghi nhật ký.

/clean
- Làm sạch các tệp và nhật ký Temp.
"""
# Add Sudo Users!


@app.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
async def useradd(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "Trả lời tin nhắn của người dùng hoặc cung cấp tên người dùng / user_id."
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id in SUDOERS:
            return await message.reply_text(
                f"{user.mention} đã là một người dùng sudo."
            )
        added = await add_sudo(user.id)
        if added:
            await message.reply_text(
                f"Thêm **{user.mention}** cho Người dùng Sudo."
            )
            os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
        else:
            await message.reply_text("Thất bại")
        return
    if message.reply_to_message.from_user.id in SUDOERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} đã là một người dùng sudo."
        )
    added = await add_sudo(message.reply_to_message.from_user.id)
    if added:
        await message.reply_text(
            f"Thêm **{message.reply_to_message.from_user.mention}** cho Người dùng Sudo"
        )
        os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
    else:
        await message.reply_text("Thất bại")
    return


@app.on_message(filters.command("delsudo") & filters.user(OWNER_ID))
async def userdel(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "Trả lời tin nhắn của người dùng hoặc cung cấp tên người dùng/user_id."
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        if user.id not in SUDOERS:
            return await message.reply_text(f"Không phải là một phần của Bot's Sudo.")
        removed = await remove_sudo(user.id)
        if removed:
            await message.reply_text(
                f"Xoá **{user.mention}** khỏi {MUSIC_BOT_NAME}."
            )
            return os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
        await message.reply_text(f"Có gì đó không ổn đã xảy ra.")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    if user_id not in SUDOERS:
        return await message.reply_text(
            f"Không phải là một phần của {MUSIC_BOT_NAME}'s Sudo."
        )
    removed = await remove_sudo(user_id)
    if removed:
        await message.reply_text(
            f"Removed **{mention}** from {MUSIC_BOT_NAME}'s Sudo."
        )
        return os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
    await message.reply_text(f"Something wrong happened.")


@app.on_message(filters.command("sudolist"))
async def sudoers_list(_, message: Message):
    sudoers = await get_sudoers()
    text = "⭐️<u> **Tác giả:**</u>\n"
    sex = 0
    for x in OWNER_ID:
        try:
            user = await app.get_users(x)
            user = user.first_name if not user.mention else user.mention
            sex += 1
        except Exception:
            continue
        text += f"{sex}➤ {user}\n"
    smex = 0
    for count, user_id in enumerate(sudoers, 1):
        if user_id not in OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += "\n⭐️<u> **Người dùng Sudo:**</u>\n"
                sex += 1
                text += f"{sex}➤ {user}\n"
            except Exception:
                continue
    if not text:
        await message.reply_text("Không có người dùng Sudo")
    else:
        await message.reply_text(text)


### Video Limit


@app.on_message(
    filters.command(["set_video_limit", f"set_video_limit@{BOT_USERNAME}"])
    & filters.user(SUDOERS)
)
async def set_video_limit_kid(_, message: Message):
    if len(message.command) != 2:
        usage = "**Usage:**\n/set_video_limit [Number of chats allowed]"
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    try:
        limit = int(state)
    except:
        return await message.reply_text(
            "Vui lòng sử dụng số để thiết lập giới hạn."
        )
    await set_video_limit(141414, limit)
    await message.reply_text(
        f"Giới hạn tối đa cuộc gọi điện video được xác định thành {limit} nhóm."
    )


## Maintenance Yukki


@app.on_message(filters.command("baotri") & filters.user(SUDOERS))
async def maintenance(_, message):
    usage = "**Sử dụng:**\n/baotri [on|off]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "on":
        user_id = 1
        await add_on(user_id)
        await message.reply_text("Được kích hoạt để bảo trì")
    elif state == "off":
        user_id = 1
        await add_off(user_id)
        await message.reply_text("Chế độ bảo trì bị tắt")
    else:
        await message.reply_text(usage)


## Logger


@app.on_message(filters.command("logger") & filters.user(SUDOERS))
async def logger(_, message):
    if LOG_SESSION == "None":
        return await message.reply_text(
            "Không có tài khoản người ghi nhật ký được xác định.\n\nVui lòng đặt <code>LOG_SESSION</code> var và sau đó thử ghi nhật ký."
        )
    usage = "**Sử dụng:**\n/logger [on|off]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "on":
        user_id = 5
        await add_on(user_id)
        await message.reply_text("Đã bật ghi nhật ký")
    elif state == "off":
        user_id = 5
        await add_off(user_id)
        await message.reply_text("Ghi nhật ký bị vô hiệu hóa")
    else:
        await message.reply_text(usage)


## Gban Module


@app.on_message(filters.command("gban") & filters.user(SUDOERS))
async def ban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) < 2:
            await message.reply_text("**Sử dụng:**\n/gban [USERNAME | USER_ID]")
            return
        user = message.text.split(None, 2)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        if user.id == from_user.id:
            return await message.reply_text(
                "Bạn muốn gban cho mình? Thật ngu ngốc!"
            )
        elif user.id == BOT_ID:
            await message.reply_text("Tôi có nên tự chặn không? Lmao Ded!")
        elif user.id in SUDOERS:
            await message.reply_text("Bạn muốn chặn một người dùng sudo? KIDXZ")
        else:
            await add_gban_user(user.id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"**Đã thêm {user.mention} vào danh sách đen!**"
            )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user.id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
__**CẬP NHẬT BLACKLIST**__
**Người dùng:** {user.mention} // `{user.id}`
**Tổng nhóm bị cấm:** {number_of_chats} nhóm"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
        return
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await message.reply_text("Bạn muốn chặn chính mình? Làm thế nào ngu ngốc!")
    elif user_id == BOT_ID:
        await message.reply_text("Tôi có nên tự chặn không? Lmao Ded!")
    elif user_id in sudoers:
        await message.reply_text("Bạn muốn chặn một người dùng sudo? KIDXZ")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await message.reply_text("Đã bị cấm.")
        else:
            await add_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"**Đang thêm {mention} vào danh sách đen!**"
            )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
__**CẬP NHẬT BLACKLIST**__
**Người dùng:** {mention} // `{user_id}`
**Đã bị cấm tổng:** {number_of_chats} nhóm"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
            return


@app.on_message(filters.command("ungban") & filters.user(SUDOERS))
async def unban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "**Sử dụng:**\n/ungban [USERNAME | USER_ID]"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        sudoers = await get_sudoers()
        if user.id == from_user.id:
            await message.reply_text("Bạn muốn bỏ chặn chính mình?")
        elif user.id == BOT_ID:
            await message.reply_text("Tôi có nên tự mở khóa không?")
        elif user.id in sudoers:
            await message.reply_text("Người dùng Sudo không thể bị chặn / bỏ chặn.")
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await message.reply_text("Anh ấy đã tự do rồi, tại sao lại bắt nạt anh ấy?")
            else:
                await remove_gban_user(user.id)
                await message.reply_text(f"Đã xoá khỏi blacklist!")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await message.reply_text("Bạn muốn bỏ chặn chính mình?")
    elif user_id == BOT_ID:
        await message.reply_text(
            "Tôi có nên tự mở khóa không? Nhưng tôi không bị chặn."
        )
    elif user_id in sudoers:
        await message.reply_text("Người dùng Sudo không thể bị chặn / bỏ chặn.")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await message.reply_text("Anh ấy đã tự do rồi, tại sao lại bắt nạt anh ấy?")
        else:
            await remove_gban_user(user_id)
            await message.reply_text(f"Đã xoá khỏi blacklist!!")


# Broadcast Message


@app.on_message(filters.command("broadcast_pin") & filters.user(SUDOERS))
async def broadcast_message_pin_silent(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                try:
                    await m.pin(disable_notification=True)
                    pin += 1
                except Exception:
                    pass
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(
            f"**Truyền tin nhắn trong {sent} nhóm với {pin} bài đã ghim.**"
        )
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Sử dụng**:\n/broadcast [MESSAGE] or [Reply to a Message]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    pin = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            try:
                await m.pin(disable_notification=True)
                pin += 1
            except Exception:
                pass
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(
        f"**Truyền tin nhắn trong {sent}nhóm và {pin} bài đã ghim.**"
    )


@app.on_message(filters.command("broadcast_pin_loud") & filters.user(SUDOERS))
async def broadcast_message_pin_loud(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                try:
                    await m.pin(disable_notification=False)
                    pin += 1
                except Exception:
                    pass
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(
            f"**Truyền tin nhắn trong {sent}  nhóm và {pin} bài đã ghim.**"
        )
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Sử dụng**:\n/broadcast [MESSAGE] or [Reply to a Message]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    pin = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            try:
                await m.pin(disable_notification=False)
                pin += 1
            except Exception:
                pass
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(
        f"**Broadcasted Message In {sent} Chats and {pin} Pins.**"
    )


@app.on_message(filters.command("broadcast") & filters.user(SUDOERS))
async def broadcast(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(f"**Truyền tin nhắn trong {sent} nhóm.**")
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Sử dụng**:\n/broadcast [MESSAGE] or [Reply to a Message]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(f"**Truyền tin nhắn trong {sent} nhóm.**")


# Clean


@app.on_message(filters.command("clean") & filters.user(SUDOERS))
async def clean(_, message):
    dir = "downloads"
    dir1 = "cache"
    shutil.rmtree(dir)
    shutil.rmtree(dir1)
    os.mkdir(dir)
    os.mkdir(dir1)
    await message.reply_text("Đã làm sạch thành công tất cả **temp** dir(s)!")
